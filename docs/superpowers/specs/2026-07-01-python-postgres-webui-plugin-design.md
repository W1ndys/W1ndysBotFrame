# W1ndysBotFrame Python + PostgreSQL + WebUI 插件化重构设计

日期：2026-07-01

## 1. 背景与目标

W1ndysBotFrame 当前已经是基于 Python 和 NapCat 的 QQ 机器人框架，但运行时架构仍然偏脚本式：

- `app/main.py` 负责 `.env` 校验和无限重连循环。
- `app/bot.py` 直接使用 `websockets.connect` 连接 NapCat，并把每条消息交给 `EventHandler`。
- `app/handle_events.py` 硬编码核心模块，再扫描 `app/modules/*/main.py`，要求模块提供 `async handle_events(websocket, msg)`。
- 所有 handler 都收到所有原始 WebSocket 消息，模块内部自行判断是否处理。
- `app/config.py` 在 import 时从 `.env` 读取常量，不适合热更新。
- `app/core/switch/database.py` 和 `app/modules/Reporter/handlers/data_manager.py` 使用 SQLite，数据模型分散。

本次重构目标是把项目升级为：

- 使用 `uv` 管理 Python 项目、依赖和虚拟环境。
- 使用 PostgreSQL 作为统一运行时存储。
- 提供 FastAPI 内置 WebUI 管理后台。
- 使用新插件协议加载模块，增删模块无需侵入式修改核心代码。
- 支持配置实时热更新。
- 支持插件代码通过 WebUI 或管理命令手动 reload。
- 不兼容旧的 `handle_events(websocket, msg)` 模块协议，现有模块需要迁移到新插件协议。

## 2. 总体架构

采用全新内核路线：新代码直接放在 `src/` 下，不再套 `src/w1ndysbot/` 包名目录。旧 `app/` 在迁移期间只作为参考来源，不继续扩展旧模块协议。

目标目录结构：

```text
src/
├── main.py                 # 新启动入口
├── runtime/                # 应用生命周期、服务编排、任务监督
├── bot/                    # NapCat WebSocket 客户端与 OneBot API client
├── events/                 # 标准事件模型、事件总线、路由和过滤器
├── plugins/                # 插件协议、加载器、注册表、上下文、重载
├── config/                 # PostgreSQL 配置服务、热更新监听
├── db/                     # SQLAlchemy async、Alembic、Repository
├── web/                    # FastAPI 内置管理后台
└── core_plugins/           # 框架内置插件：菜单、开关、在线检测、Reporter 等
```

运行时数据流：

```text
NapCat WebSocket
      ↓
bot.napcat_client
      ↓
events.event_parser
      ↓
events.router
      ↓
plugins.manager
      ↓
具体插件 handle_event()
```

WebUI 不直接绕过服务层修改内存状态，而是优先写 PostgreSQL；配置或插件状态变化后通过 PostgreSQL `LISTEN/NOTIFY` 通知运行时刷新。

## 3. uv 与项目工程化

项目从 `requirements.txt` 迁移到 `pyproject.toml` + `uv.lock`。

建议依赖：

- `fastapi`
- `uvicorn`
- `jinja2`
- `websockets`
- `sqlalchemy[asyncio]`
- `asyncpg`
- `alembic`
- `pydantic`
- `pydantic-settings`
- `python-dotenv`
- `loguru`
- `pytest`
- `pytest-asyncio`
- `httpx`

建议启动方式：

```bash
uv sync
uv run python src/main.py
```

后续可在 `pyproject.toml` 中配置脚本，例如：

```bash
uv run bot
```

`.env` 只保留启动必需配置：

```env
DATABASE_URL=postgresql+asyncpg://user:password@127.0.0.1:5432/w1ndys_bot_frame
WEBUI_SECRET_KEY=change-me
BOOTSTRAP_ADMIN_PASSWORD=change-me
```

## 4. PostgreSQL 数据设计

数据库统一使用 PostgreSQL + SQLAlchemy async + Alembic。

### 4.1 `app_settings`

保存框架级运行时配置。

```text
id uuid primary key
namespace text not null
key text not null
value jsonb not null
schema_version int not null default 1
updated_at timestamptz not null
updated_by text
unique(namespace, key)
```

示例配置：

- `bot.owner_id`
- `bot.ws_url`
- `bot.token`
- `logging.level`
- `webui.site_title`

### 4.2 `plugin_registry`

保存插件注册和加载状态。

```text
name text primary key
version text not null
description text
entrypoint text not null
enabled bool not null default false
load_state text not null
last_loaded_at timestamptz
last_error text
created_at timestamptz not null
updated_at timestamptz not null
```

### 4.3 `plugin_config`

保存插件配置。

```text
plugin_name text references plugin_registry(name)
key text not null
value jsonb not null
updated_at timestamptz not null
primary key(plugin_name, key)
```

### 4.4 `plugin_switches`

替代当前 SQLite `module_switches`。

```text
plugin_name text references plugin_registry(name)
scope_type text not null  -- global / group / private
scope_id text             -- group_id 或 user_id，全局为空
enabled bool not null
updated_at timestamptz not null
unique(plugin_name, scope_type, scope_id)
```

### 4.5 `message_mappings`

替代 Reporter 当前 SQLite 存储。

```text
id uuid primary key
original_sender_id text not null
original_message_id text not null
forwarded_message_id text unique
raw_message jsonb
created_at timestamptz not null
updated_at timestamptz not null
```

### 4.6 `plugin_error_logs` 和 `event_logs`

用于 WebUI 排查问题。

```text
plugin_error_logs:
- plugin_name
- event_id
- error_type
- message
- traceback
- created_at

event_logs:
- event_type
- source
- payload jsonb
- received_at
```

## 5. 配置热更新

配置修改统一走 `ConfigService`：

```text
WebUI 表单提交
      ↓
ConfigService 校验并写入 PostgreSQL
      ↓
提交事务
      ↓
NOTIFY config_changed, '{"namespace":"plugin","key":"xxx"}'
      ↓
运行时 ConfigListener 收到通知
      ↓
重新从数据库读取对应配置
      ↓
通知相关插件 on_config_update()
```

第一版配置分两类。

### 5.1 可实时生效

- 插件启用/禁用状态
- 插件配置
- 群/私聊开关
- 管理员 ID 列表
- 日志等级
- 菜单显示配置

### 5.2 需要重连或重启

- NapCat WebSocket 地址
- NapCat token
- PostgreSQL 连接
- WebUI 监听 host/port
- WebUI session secret

WebUI 对第二类配置显示“已保存，需重连/重启生效”，并提供手动重连按钮，不静默断开重连。

`LISTEN/NOTIFY` 不是持久队列，因此运行时收到通知后必须以数据库为准重新读取；同时保留周期性版本校验，避免漏通知导致状态长期不一致。

## 6. 新插件协议

第一版采用全新插件协议，不兼容旧的：

```python
async def handle_events(websocket, msg)
```

插件应实现明确的元数据、订阅和生命周期。

示例结构：

```python
class MyPlugin:
    meta = PluginMeta(
        name="reporter",
        version="1.0.0",
        description="消息转发与回复映射",
        subscriptions=[
            EventSubscription(
                event_type="message",
                message_type="private",
                priority=100,
            )
        ],
        config_schema=ReporterConfig,
    )

    async def setup(self, ctx: PluginContext) -> None:
        ...

    async def handle_event(self, event: BotEvent, ctx: PluginContext) -> PluginResult:
        ...

    async def on_config_update(self, config) -> None:
        ...

    async def teardown(self) -> None:
        ...
```

插件目录：

```text
src/core_plugins/     # 框架内置插件
plugins/              # 用户/第三方插件，可选外置目录
```

内置插件优先迁移：

- `switch`
- `menu`
- `online_detect`
- `del_self_msg`
- `get_group_list`
- `get_group_member_list`
- `nc_get_rkey`
- `reporter`

### 6.1 PluginContext

插件不直接持有原始 websocket，而是通过上下文访问能力：

```text
ctx.api          # OneBot/NapCat API client
ctx.db           # async DB session/repository
ctx.config       # 插件配置与全局配置访问
ctx.logger       # 插件专属 logger
ctx.scheduler    # 后台任务/定时任务注册
ctx.permissions  # 管理员/群管理员校验
```

### 6.2 PluginResult

插件返回结构化结果：

```text
handled: bool
stop_propagation: bool
errors: list
```

这样 EventRouter 可以明确知道是否继续向后传播事件。

## 7. 事件模型与分发

原始 NapCat/OneBot JSON 只在网关层出现一次，之后转成标准事件：

```text
BotEvent
├── MessageEvent
│   ├── PrivateMessageEvent
│   └── GroupMessageEvent
├── NoticeEvent
├── RequestEvent
├── MetaEvent
└── ApiResponseEvent
```

EventRouter 根据插件订阅条件分发事件，不再广播给所有插件。

第一版匹配条件保持简单：

- `event_type`
- `message_type`
- `command_prefix`
- `priority`
- `scope`

事件执行策略：

- 支持插件优先级。
- 插件异常不影响其他插件。
- 每个插件执行有 timeout。
- 记录 `plugin_error_logs`。
- 支持 `stop_propagation` 中止后续插件处理。
- 对高频事件保留并发限制，避免无限 `asyncio.create_task`。

## 8. 插件手动 reload

第一版插件代码不做文件监听自动热更新，只支持 WebUI 或管理命令手动 reload。

推荐安全 reload 流程：

```text
WebUI 点击 Reload / 管理命令触发
      ↓
PluginManager 标记插件 reloading
      ↓
先加载新插件实例
      ↓
新实例 setup() 成功
      ↓
从路由表原子替换旧实例
      ↓
停止旧插件注册的后台任务
      ↓
调用旧实例 teardown()
      ↓
更新 plugin_registry 状态
```

如果新实例加载失败，保留旧实例继续运行，并把错误写入 `plugin_registry.last_error` 和 `plugin_error_logs`。

## 9. FastAPI 内置 WebUI

第一版采用 FastAPI + Jinja2 服务端渲染页面，不引入独立 Vue/React SPA。

目录：

```text
src/web/
├── app.py
├── deps.py
├── auth.py
├── routes/
│   ├── dashboard.py
│   ├── config.py
│   ├── plugins.py
│   ├── logs.py
│   └── health.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── config.html
│   ├── plugins.html
│   ├── plugin_detail.html
│   ├── logs.html
│   └── health.html
└── static/
```

页面：

- Dashboard：机器人状态、NapCat 连接状态、插件数量、最近错误。
- Config：全局配置、插件配置编辑。
- Plugins：插件列表、启用/禁用、手动 reload、错误状态。
- Plugin Detail：插件元数据、订阅事件、配置表单、开关配置。
- Logs：应用日志、插件错误日志、事件日志筛选。
- Health：PostgreSQL、NapCat、ConfigListener、后台任务状态。

路由示例：

```text
GET  /
GET  /config
POST /config/{namespace}/{key}
GET  /plugins
GET  /plugins/{name}
POST /plugins/{name}/enable
POST /plugins/{name}/disable
POST /plugins/{name}/reload
GET  /logs
GET  /health
GET  /api/health
```

WebUI 安全默认策略：

- 默认绑定 `127.0.0.1`。
- 管理员登录。
- signed session cookie。
- POST 表单加 CSRF token。
- 不在页面明文展示 token/secret。
- 外网访问必须由用户主动修改配置。

## 10. 分阶段实施路线

### Phase 0：设计确认

- 提交本设计文档。
- 明确新内核目录为 `src/`。
- 明确不兼容旧模块协议。
- 明确 WebUI 第一版为 FastAPI 内置页面。
- 明确配置实时热更新，代码手动 reload。
- 明确 PostgreSQL 为统一运行时存储。

### Phase 1：工程骨架

- 新增 `pyproject.toml`。
- 迁移到 `uv`。
- 新建 `src/` 目标结构。
- 建立 `src/main.py`、runtime skeleton、测试目录。
- 保留旧 `app/` 作为迁移参考。

验证：

```bash
uv sync
uv run python src/main.py --help
uv run pytest
```

### Phase 2：数据库基础

- SQLAlchemy async session。
- Alembic 初始化。
- 建核心表 migration。
- Repository/Service 基础层。

验证：

```bash
uv run alembic upgrade head
uv run pytest tests/unit/db tests/integration/db
```

### Phase 3：NapCat 网关与事件模型

- 重写 WebSocket client。
- 标准事件模型。
- OneBot API client。
- reconnect/backoff。

验证：

- fake WebSocket 测试。
- raw JSON → typed event 单元测试。
- API client payload 测试。

### Phase 4：插件系统

- `PluginMeta`。
- `PluginContext`。
- `PluginManager`。
- `EventRouter`。
- 手动 reload。
- 插件错误隔离。

验证：

- 插件加载成功/失败测试。
- 事件订阅匹配测试。
- reload 失败不影响旧实例测试。
- `plugin_error_logs` 写入测试。

### Phase 5：配置热更新

- `ConfigService`。
- PostgreSQL `LISTEN/NOTIFY` listener。
- WebUI 修改配置触发运行时刷新。
- 插件 `on_config_update`。

验证：

- 修改配置后运行时快照更新。
- 插件收到配置更新。
- 需要重连的配置不会被静默应用。

### Phase 6：WebUI v1

- Dashboard。
- Config。
- Plugins。
- Logs。
- Health。
- 登录鉴权和 CSRF。

验证：

```bash
uv run pytest tests/integration/web
```

并手动访问：

```text
http://127.0.0.1:<port>/
```

### Phase 7：迁移核心功能为内置插件

优先迁移：

1. switch
2. menu
3. online_detect
4. del_self_msg
5. get_group_list
6. get_group_member_list
7. nc_get_rkey
8. reporter

### Phase 8：文档与迁移指南

- 重写开发文档。
- 新插件模板。
- 旧模块迁移指南。
- PostgreSQL / uv / WebUI 启动说明。

## 11. 风险与处理

### 11.1 插件 reload 状态泄露

处理方式：

- 插件后台任务必须通过 `ctx.scheduler` 注册。
- reload 时统一取消旧插件任务。
- 新实例 setup 成功后再替换旧实例。
- reload 失败时保留旧实例继续运行。

### 11.2 配置通知丢失

处理方式：

- `NOTIFY` 只作为变更信号。
- 收到通知后总是从数据库重新读取。
- 增加周期性版本校验。

### 11.3 WebUI 安全

处理方式：

- 默认 localhost。
- 登录鉴权。
- session cookie 签名。
- POST CSRF。
- secret 不明文展示。

### 11.4 旧模块迁移成本

处理方式：

- 不做旧协议兼容层，避免长期维护成本。
- 提供新插件模板和迁移指南。
- 优先迁移框架内置核心功能。

### 11.5 PostgreSQL 运维成本

处理方式：

- 提供本地 Docker Compose 示例。
- 文档中明确 `DATABASE_URL` 配置。
- 测试中使用独立测试库。

## 12. 验收标准

最终重构完成时至少满足：

- `uv sync` 成功。
- `uv run pytest` 成功。
- PostgreSQL migration 可从空库创建完整 schema。
- WebUI 可登录。
- WebUI 可启用/禁用插件。
- WebUI 可修改插件配置，并实时通知运行时。
- 插件 reload 失败不会拖垮机器人。
- NapCat 断线后可自动重连。
- 核心插件能处理群聊/私聊消息。
- switch/menu/reporter 行为迁移完成。
- 文档明确旧 `app/modules/*/main.py handle_events(websocket, msg)` 协议不再兼容。
