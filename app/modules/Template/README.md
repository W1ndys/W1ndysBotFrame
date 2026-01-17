# Template 模块

模板模块是 W1ndysBotFrame 框架中用于快速创建新功能模块的基础结构。通过复制和修改此模板，开发者可以方便地实现自己的功能模块。

## 目录结构

```
Template/
├── __init__.py                    # 模块配置
├── main.py                        # 事件处理入口
├── README.md                      # 模块说明
└── handlers/                      # 事件处理器目录
    ├── handle_meta_event.py       # 元事件处理（心跳等）
    ├── handle_message.py          # 消息分发
    ├── handle_message_group.py    # 群消息处理
    ├── handle_message_private.py  # 私聊消息处理
    ├── handle_notice.py           # 通知事件分发
    ├── handle_notice_group.py     # 群通知处理
    ├── handle_notice_friend.py    # 好友通知处理
    ├── handle_request.py          # 请求事件处理
    ├── handle_response.py         # API响应处理
    └── data_manager.py            # 数据库管理
```

## 使用方法

### 1. 复制模板

```bash
cd app/modules
cp -r Template MyModule
```

### 2. 修改配置

编辑 `__init__.py`：

```python
MODULE_NAME = "MyModule"       # 模块名称
SWITCH_NAME = "mm"             # 开关命令
MODULE_DESCRIPTION = "我的模块" # 模块描述
BASE_COMMAND = "/mm"           # 主命令
```

### 3. 实现业务逻辑

主要在 `handlers/handle_message_group.py` 和 `handlers/handle_message_private.py` 中实现消息处理逻辑。

## 核心文件说明

### `__init__.py`

定义模块的基础配置：

- `MODULE_NAME`: 模块标识名
- `SWITCH_NAME`: 开关控制命令
- `DATA_DIR`: 数据存储目录
- `COMMANDS`: 命令列表

### `main.py`

模块入口，必须提供 `async handle_events(websocket, msg)` 函数。

### `handlers/handle_message_group.py`

群消息处理示例，包含：

- 开关命令处理
- 菜单命令处理
- 开关状态检查
- 消息处理逻辑

### `handlers/data_manager.py`

SQLite 数据库管理类，支持 with 语句自动关闭连接。

## 开关系统

每个模块支持独立的群聊/私聊开关：

- 发送 `SWITCH_NAME`（如 `tp`）切换开关
- 发送 `SWITCH_NAME菜单`（如 `tp菜单`）查看命令列表

## 详细文档

- [开发指南](../../../docs/development.md)
- [API 参考](../../../docs/api-reference.md)
