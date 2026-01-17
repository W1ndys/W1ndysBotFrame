# 开发指南

本文档详细介绍如何基于 W1ndysBotFrame 框架开发功能模块。

## 目录

- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [模块开发规范](#模块开发规范)
- [事件处理](#事件处理)
- [开关系统](#开关系统)
- [数据存储](#数据存储)
- [权限认证](#权限认证)
- [消息发送](#消息发送)
- [定时任务](#定时任务)
- [最佳实践](#最佳实践)

---

## 项目结构

```
W1ndysBotFrame/
├── app/                          # 核心应用目录
│   ├── main.py                   # 程序入口
│   ├── bot.py                    # WebSocket连接管理
│   ├── config.py                 # 配置加载模块
│   ├── handle_events.py          # 事件处理器（模块加载/分发）
│   ├── logger.py                 # 日志系统
│   ├── .env.example              # 环境变量示例
│   ├── api/                      # API接口封装
│   │   ├── message.py            # 消息API
│   │   ├── group.py              # 群管理API
│   │   ├── user.py               # 用户API
│   │   └── key.py                # 密钥API
│   ├── core/                     # 核心功能模块
│   │   ├── switchs.py            # 开关系统
│   │   ├── menu_manager.py       # 菜单管理器
│   │   └── ...                   # 其他核心功能
│   ├── utils/                    # 工具函数
│   │   ├── auth.py               # 权限认证
│   │   ├── generate.py           # 消息段生成器
│   │   └── ...                   # 其他工具
│   ├── modules/                  # 功能模块目录
│   │   └── Template/             # 模板模块（开发示例）
│   └── data/                     # 数据存储目录
├── requirements.txt              # Python依赖
└── README.md                     # 项目说明
```

---

## 快速开始

### 1. 创建模块目录

在 `app/modules/` 下创建你的模块目录：

```bash
cd app/modules
mkdir MyModule
```

### 2. 创建必需文件

每个模块至少需要两个文件：

```
modules/MyModule/
├── __init__.py          # 模块配置（必需）
└── main.py              # 入口文件（必需）
```

### 3. 配置模块 (`__init__.py`)

```python
import os

# 模块名称（用于日志和开关系统标识）
MODULE_NAME = "MyModule"

# 模块开关名称（用户发送此命令切换开关）
SWITCH_NAME = "mm"

# 模块描述
MODULE_DESCRIPTION = "我的模块"

# 数据目录（自动创建）
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

# 命令定义
BASE_COMMAND = "/mm"  # 主命令

COMMANDS = {
    BASE_COMMAND: "主命令说明",
    f"{BASE_COMMAND} help": "查看帮助",
    # 可以继续添加其他命令
}
```

### 4. 创建入口文件 (`main.py`)

```python
from logger import logger
from . import MODULE_NAME

async def handle_events(websocket, msg):
    """统一事件处理入口（必需函数）

    Args:
        websocket: WebSocket连接对象
        msg: 接收到的消息字典
    """
    try:
        post_type = msg.get("post_type", "")

        # 处理消息事件
        if post_type == "message":
            await handle_message(websocket, msg)

    except Exception as e:
        logger.error(f"[{MODULE_NAME}]处理事件失败: {e}")

async def handle_message(websocket, msg):
    """处理消息事件"""
    message_type = msg.get("message_type", "")

    if message_type == "group":
        # 处理群消息
        pass
    elif message_type == "private":
        # 处理私聊消息
        pass
```

---

## 模块开发规范

### 推荐目录结构

参考 `Template` 模块的完整结构：

```
modules/MyModule/
├── __init__.py                    # 模块配置
├── main.py                        # 入口文件
├── README.md                      # 模块说明
└── handlers/                      # 事件处理器
    ├── handle_message.py          # 消息分发
    ├── handle_message_group.py    # 群消息处理
    ├── handle_message_private.py  # 私聊消息处理
    ├── handle_meta_event.py       # 元事件处理
    ├── handle_notice.py           # 通知事件处理
    ├── handle_notice_group.py     # 群通知处理
    ├── handle_notice_friend.py    # 好友通知处理
    ├── handle_request.py          # 请求事件处理
    ├── handle_response.py         # 响应处理
    └── data_manager.py            # 数据管理
```

### 完整的 `main.py` 示例

```python
from logger import logger
from . import MODULE_NAME
from .handlers.handle_meta_event import MetaEventHandler
from .handlers.handle_message import MessageHandler
from .handlers.handle_notice import NoticeHandler
from .handlers.handle_request import RequestHandler
from .handlers.handle_response import ResponseHandler

async def handle_events(websocket, msg):
    """统一事件处理入口"""
    try:
        # 处理API响应事件
        if msg.get("status") == "ok":
            await ResponseHandler(websocket, msg).handle()
            return

        # 基于事件类型分发
        post_type = msg.get("post_type", "")

        if post_type == "meta_event":
            await MetaEventHandler(websocket, msg).handle()
        elif post_type == "message":
            await MessageHandler(websocket, msg).handle()
        elif post_type == "notice":
            await NoticeHandler(websocket, msg).handle()
        elif post_type == "request":
            await RequestHandler(websocket, msg).handle()

    except Exception as e:
        logger.error(f"[{MODULE_NAME}]处理事件失败: {e}")
```

---

## 事件处理

### 事件类型

框架支持处理以下事件类型：

| 事件类型 | `post_type` | 说明 |
|---------|-------------|------|
| 消息事件 | `message` | 群聊/私聊消息 |
| 通知事件 | `notice` | 群成员变动、好友变动等 |
| 请求事件 | `request` | 加群、加好友请求 |
| 元事件 | `meta_event` | 心跳、生命周期事件 |
| API响应 | `status: "ok"` | API调用响应 |

### 消息事件 (`message`)

消息事件包含以下字段：

```python
msg = {
    "post_type": "message",
    "message_type": "group",       # group/private
    "sub_type": "normal",          # 子类型
    "message_id": 123456,          # 消息ID
    "group_id": 123456789,         # 群号（群消息）
    "user_id": 987654321,          # 发送者QQ
    "message": [...],              # 消息段数组
    "raw_message": "文本内容",      # 原始文本消息
    "sender": {                    # 发送者信息
        "nickname": "昵称",
        "card": "群名片",
        "role": "owner/admin/member"
    },
    "time": 1234567890             # 时间戳
}
```

### 通知事件 (`notice`)

| 通知类型 | `notice_type` | 说明 |
|---------|---------------|------|
| 群文件上传 | `group_upload` | 群文件上传 |
| 群管理员变动 | `group_admin` | 管理员设置/取消 |
| 群成员减少 | `group_decrease` | 主动退群/被踢 |
| 群成员增加 | `group_increase` | 主动入群/被邀请 |
| 群禁言 | `group_ban` | 禁言/解除禁言 |
| 好友添加 | `friend_add` | 好友添加成功 |
| 群消息撤回 | `group_recall` | 群消息撤回 |
| 好友消息撤回 | `friend_recall` | 好友消息撤回 |
| 戳一戳 | `notify` (poke) | 戳一戳通知 |
| 群精华消息 | `essence` | 精华消息变动 |

### 请求事件 (`request`)

| 请求类型 | `request_type` | 说明 |
|---------|----------------|------|
| 好友请求 | `friend` | 加好友请求 |
| 群请求 | `group` | 加群/邀请入群请求 |

---

## 开关系统

每个模块可以通过开关系统实现群/私聊独立控制。

### 导入开关函数

```python
from core.switchs import (
    is_group_switch_on,       # 检查群开关状态
    is_private_switch_on,     # 检查私聊开关状态
    toggle_group_switch,      # 切换群开关
    toggle_private_switch,    # 切换私聊开关
    handle_module_group_switch,   # 处理群开关命令
    handle_module_private_switch, # 处理私聊开关命令
)
```

### 使用示例

```python
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin
from .. import MODULE_NAME, SWITCH_NAME

class GroupMessageHandler:
    async def handle(self):
        # 1. 处理开关命令（管理员可切换开关）
        if self.raw_message.lower() == SWITCH_NAME.lower():
            if is_system_admin(self.user_id):
                await handle_module_group_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.group_id,
                    self.message_id,
                )
            return

        # 2. 检查开关状态
        if not is_group_switch_on(self.group_id, MODULE_NAME):
            return  # 开关关闭，不处理

        # 3. 处理业务逻辑
        await self.process_message()
```

### 开关命令格式

- 切换群开关：发送模块的 `SWITCH_NAME`（如 `tp`）
- 查看模块菜单：发送 `SWITCH_NAME` + `菜单`（如 `tp菜单`）

---

## 数据存储

### 数据目录规范

数据文件应存放在 `app/data/<模块名>/` 目录下：

```python
import os
from . import MODULE_NAME

# 方式1：使用模块配置的 DATA_DIR
from . import DATA_DIR
file_path = os.path.join(DATA_DIR, "config.json")

# 方式2：手动构建路径
data_dir = os.path.join("data", MODULE_NAME)
os.makedirs(data_dir, exist_ok=True)
```

### 数据库操作（SQLite）

推荐使用 `DataManager` 类管理数据库连接：

```python
import sqlite3
import os
from .. import MODULE_NAME

class DataManager:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"{MODULE_NAME}.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """初始化表结构"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS my_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

# 使用示例
with DataManager() as dm:
    dm.cursor.execute("INSERT INTO my_data (group_id, content) VALUES (?, ?)",
                      ("123456", "test"))
    dm.conn.commit()
```

### JSON 数据存储

```python
import json
import os
from . import DATA_DIR

def save_data(filename, data):
    """保存数据到JSON文件"""
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(filename, default=None):
    """从JSON文件加载数据"""
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else {}
```

---

## 权限认证

### 系统管理员认证

```python
from utils.auth import is_system_admin

if is_system_admin(user_id):
    # 执行管理员操作
    pass
```

### 群管理员认证

```python
from utils.auth import is_group_admin

# role 从消息的 sender 字段获取
if is_group_admin(sender.get("role")):
    # 执行群管理操作
    pass
```

### 组合认证

```python
from utils.auth import is_system_admin, is_group_admin

def has_permission(user_id, role):
    """检查用户是否有权限"""
    return is_system_admin(user_id) or is_group_admin(role)
```

---

## 消息发送

详细的 API 参考请查看 [API 参考文档](./api-reference.md)。

### 快速示例

```python
from api.message import send_group_msg, send_private_msg
from utils.generate import (
    generate_text_message,
    generate_at_message,
    generate_reply_message,
    generate_image_message,
)

# 发送纯文本
await send_group_msg(websocket, group_id, "Hello World")

# 发送消息段组合
await send_group_msg(websocket, group_id, [
    generate_reply_message(message_id),  # 回复原消息
    generate_at_message(user_id),        # @用户
    generate_text_message(" 你好！"),     # 文本内容
])

# 发送图片
await send_group_msg(websocket, group_id, [
    generate_image_message("http://example.com/image.png", type="url")
])

# 发送后自动撤回（30秒后）
await send_group_msg(websocket, group_id, "临时消息", note="del_msg=30")
```

---

## 定时任务

使用 `asyncio` 实现定时任务：

```python
import asyncio
from logger import logger
from . import MODULE_NAME

async def scheduled_task(websocket):
    """定时任务示例"""
    while True:
        try:
            # 执行定时逻辑
            logger.info(f"[{MODULE_NAME}]执行定时任务")

            # 等待指定时间（秒）
            await asyncio.sleep(3600)  # 每小时执行一次

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]定时任务失败: {e}")
            await asyncio.sleep(60)  # 出错后等待1分钟重试
```

### 在模块中启动定时任务

可以在处理心跳事件时启动：

```python
class MetaEventHandler:
    _task_started = False

    async def handle(self):
        if self.meta_event_type == "heartbeat":
            if not MetaEventHandler._task_started:
                MetaEventHandler._task_started = True
                asyncio.create_task(scheduled_task(self.websocket))
```

---

## 最佳实践

### 1. 异步编程注意事项

```python
# 正确：使用 asyncio.sleep
await asyncio.sleep(1)

# 错误：会阻塞整个程序
import time
time.sleep(1)  # 不要使用！
```

### 2. 大量循环处理

```python
# 处理大量数据时，定期交出控制权
for i, item in enumerate(large_list):
    process(item)
    if i % 100 == 0:
        await asyncio.sleep(0.1)  # 每100次暂停一下
```

### 3. 错误处理

```python
from logger import logger

try:
    await some_operation()
except Exception as e:
    logger.error(f"[{MODULE_NAME}]操作失败: {e}")
    # 可选：通知管理员
```

### 4. 消息内容判断

```python
# 推荐：忽略大小写比较
if raw_message.lower() == "/help":
    pass

# 推荐：使用 startswith 判断命令前缀
if raw_message.lower().startswith("/mymodule"):
    pass
```

### 5. 安全地获取字典值

```python
# 使用 get 方法避免 KeyError
group_id = str(msg.get("group_id", ""))
user_id = str(msg.get("user_id", ""))
sender = msg.get("sender", {})
nickname = sender.get("nickname", "未知")
```

### 6. 模块间解耦

- 模块应该独立运行，避免模块间直接调用
- 共享功能应放在 `utils/` 或 `core/` 目录
- 使用事件机制而非直接调用

---

## 调试技巧

### 查看日志

日志文件位于 `app/logs/` 目录，按日期分类：

```bash
tail -f app/logs/YYYY-MM-DD.log
```

### 使用 logger 输出调试信息

```python
from logger import logger

logger.debug(f"调试信息: {variable}")
logger.info(f"普通信息")
logger.warning(f"警告信息")
logger.error(f"错误信息")
```

### 模块加载检查

启动后，机器人会私聊管理员发送模块加载状态报告，包括：
- 成功加载的模块列表
- 加载失败的模块及原因

---

## 参考链接

- [NapCat 官方文档](https://napneko.github.io/)
- [OneBot 11 协议](https://11.onebot.dev/)
- [API 参考文档](./api-reference.md)
