# API 参考文档

本文档详细介绍 W1ndysBotFrame 框架提供的 API 接口。

## 目录

- [消息 API](#消息-api)
- [群管理 API](#群管理-api)
- [用户 API](#用户-api)
- [消息段生成器](#消息段生成器)
- [开关系统 API](#开关系统-api)
- [权限认证 API](#权限认证-api)

---

## 消息 API

位置：`app/api/message.py`

### send_group_msg

发送群聊消息。

```python
from api.message import send_group_msg

await send_group_msg(websocket, group_id, message, note="")
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `websocket` | WebSocket | 是 | WebSocket 连接对象 |
| `group_id` | int/str | 是 | 目标群号 |
| `message` | str/dict/list | 是 | 消息内容 |
| `note` | str | 否 | 附加说明，支持 `del_msg=秒数` |

**message 参数格式：**

- `str`: 纯文本消息
- `dict`: 单个消息段对象
- `list`: 消息段数组

**示例：**

```python
# 发送纯文本
await send_group_msg(websocket, 123456789, "Hello World")

# 发送消息段
await send_group_msg(websocket, 123456789, [
    {"type": "text", "data": {"text": "Hello"}}
])

# 发送后30秒自动撤回
await send_group_msg(websocket, 123456789, "临时消息", note="del_msg=30")
```

---

### send_private_msg

发送私聊消息。

```python
from api.message import send_private_msg

await send_private_msg(websocket, user_id, message, note="")
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `websocket` | WebSocket | 是 | WebSocket 连接对象 |
| `user_id` | int/str | 是 | 目标用户QQ号 |
| `message` | str/dict/list | 是 | 消息内容 |
| `note` | str | 否 | 附加说明 |

---

### send_group_msg_with_cq

使用 CQ 码格式发送群消息（旧格式）。

```python
from api.message import send_group_msg_with_cq

await send_group_msg_with_cq(websocket, group_id, content, note="")
```

---

### send_private_msg_with_cq

使用 CQ 码格式发送私聊消息（旧格式）。

```python
from api.message import send_private_msg_with_cq

await send_private_msg_with_cq(websocket, user_id, content, note="")
```

---

### delete_msg

撤回消息。

```python
from api.message import delete_msg

await delete_msg(websocket, message_id)
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `message_id` | int | 是 | 要撤回的消息ID |

---

### get_msg

获取消息详情。

```python
from api.message import get_msg

await get_msg(websocket, message_id)
```

---

### get_group_msg_history

获取群消息历史记录。

```python
from api.message import get_group_msg_history

await get_group_msg_history(websocket, group_id, message_seq=None, count=20)
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `group_id` | int | 是 | 群号 |
| `message_seq` | int | 否 | 起始消息序号 |
| `count` | int | 否 | 获取数量，默认20 |

---

### send_forward_msg

发送合并转发消息。

```python
from api.message import send_forward_msg

await send_forward_msg(websocket, group_id, messages)
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `group_id` | int | 是 | 群号 |
| `messages` | list | 是 | 合并转发节点数组 |

**示例：**

```python
from utils.generate import generate_node_message, generate_text_message

messages = [
    generate_node_message(10001, "用户1", [generate_text_message("第一条消息")]),
    generate_node_message(10002, "用户2", [generate_text_message("第二条消息")]),
]
await send_forward_msg(websocket, group_id, messages)
```

---

### group_poke

发送群戳一戳。

```python
from api.message import group_poke

await group_poke(websocket, group_id, user_id)
```

---

## 群管理 API

位置：`app/api/group.py`

### set_group_kick

踢出群成员。

```python
from api.group import set_group_kick

await set_group_kick(websocket, group_id, user_id, reject_add_request=False)
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `group_id` | int | 是 | 群号 |
| `user_id` | int | 是 | 要踢的用户QQ号 |
| `reject_add_request` | bool | 否 | 是否拒绝再次加群，默认False |

---

### set_group_ban

禁言群成员。

```python
from api.group import set_group_ban

await set_group_ban(websocket, group_id, user_id, duration=600)
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `group_id` | int | 是 | 群号 |
| `user_id` | int | 是 | 要禁言的用户QQ号 |
| `duration` | int | 否 | 禁言时长（秒），0表示解除禁言 |

---

### set_group_whole_ban

设置全员禁言。

```python
from api.group import set_group_whole_ban

await set_group_whole_ban(websocket, group_id, enable=True)
```

---

### set_group_admin

设置群管理员。

```python
from api.group import set_group_admin

await set_group_admin(websocket, group_id, user_id, enable=True)
```

---

### set_group_card

设置群名片。

```python
from api.group import set_group_card

await set_group_card(websocket, group_id, user_id, card="新名片")
```

---

### set_group_name

设置群名称。

```python
from api.group import set_group_name

await set_group_name(websocket, group_id, group_name="新群名")
```

---

### set_group_leave

退出群聊。

```python
from api.group import set_group_leave

await set_group_leave(websocket, group_id, is_dismiss=False)
```

---

### get_group_info

获取群信息。

```python
from api.group import get_group_info

await get_group_info(websocket, group_id, no_cache=False)
```

---

### get_group_list

获取群列表。

```python
from api.group import get_group_list

await get_group_list(websocket)
```

---

### get_group_member_info

获取群成员信息。

```python
from api.group import get_group_member_info

await get_group_member_info(websocket, group_id, user_id, no_cache=False)
```

---

### get_group_member_list

获取群成员列表。

```python
from api.group import get_group_member_list

await get_group_member_list(websocket, group_id)
```

---

### set_group_add_request

处理加群请求。

```python
from api.group import set_group_add_request

await set_group_add_request(websocket, flag, sub_type, approve=True, reason="")
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `flag` | str | 是 | 请求标识（从请求事件获取） |
| `sub_type` | str | 是 | 请求类型：`add`/`invite` |
| `approve` | bool | 否 | 是否同意，默认True |
| `reason` | str | 否 | 拒绝理由 |

---

### send_group_notice

发送群公告。

```python
from api.group import send_group_notice

await send_group_notice(websocket, group_id, content, image=None)
```

---

## 用户 API

位置：`app/api/user.py`

### get_login_info

获取登录账号信息。

```python
from api.user import get_login_info

await get_login_info(websocket)
```

---

### get_stranger_info

获取陌生人信息。

```python
from api.user import get_stranger_info

await get_stranger_info(websocket, user_id, no_cache=False)
```

---

### get_friend_list

获取好友列表。

```python
from api.user import get_friend_list

await get_friend_list(websocket)
```

---

### set_friend_add_request

处理好友请求。

```python
from api.user import set_friend_add_request

await set_friend_add_request(websocket, flag, approve=True, remark="")
```

---

## 消息段生成器

位置：`app/utils/generate.py`

### generate_text_message

生成文本消息段。

```python
from utils.generate import generate_text_message

msg = generate_text_message("Hello World")
# 返回: {"type": "text", "data": {"text": "Hello World"}}
```

---

### generate_at_message

生成 @ 消息段。

```python
from utils.generate import generate_at_message

# @指定用户
msg = generate_at_message(123456789)
# 返回: {"type": "at", "data": {"qq": 123456789}}

# @全体成员
msg = generate_at_message("all")
# 返回: {"type": "at", "data": {"qq": "all"}}
```

---

### generate_reply_message

生成回复消息段。

```python
from utils.generate import generate_reply_message

msg = generate_reply_message(message_id)
# 返回: {"type": "reply", "data": {"id": message_id}}
```

---

### generate_image_message

生成图片消息段。

```python
from utils.generate import generate_image_message

# 网络图片
msg = generate_image_message("http://example.com/image.png", type="url")

# 本地图片
msg = generate_image_message("D:/images/test.png", type="file")

# Base64图片
msg = generate_image_message("iVBORw0KGgo...", type="base64")
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `file` | str | 是 | 图片路径/URL/Base64 |
| `type` | str | 否 | 类型：`url`/`file`/`base64` |
| `cache` | bool | 否 | 是否使用缓存，默认True |
| `proxy` | bool | 否 | 是否通过代理下载，默认True |
| `timeout` | int | 否 | 下载超时时间（秒） |

---

### generate_face_message

生成 QQ 表情消息段。

```python
from utils.generate import generate_face_message

msg = generate_face_message(178)  # 表情ID
# 返回: {"type": "face", "data": {"id": 178}}
```

---

### generate_record_message

生成语音消息段。

```python
from utils.generate import generate_record_message

msg = generate_record_message(file, magic=False)
```

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `file` | str | 是 | 语音文件路径/URL/Base64 |
| `magic` | bool | 否 | 是否变声，默认False |

---

### generate_video_message

生成视频消息段。

```python
from utils.generate import generate_video_message

msg = generate_video_message(file)
```

---

### generate_poke_message

生成戳一戳消息段。

```python
from utils.generate import generate_poke_message

msg = generate_poke_message(user_id)
# 返回: {"type": "poke", "data": {"qq": user_id}}
```

---

### generate_share_message

生成链接分享消息段。

```python
from utils.generate import generate_share_message

msg = generate_share_message(
    url="https://example.com",
    title="网站标题",
    content="网站简介",  # 可选
    image="https://example.com/image.png"  # 可选
)
```

---

### generate_node_message

生成合并转发节点。

```python
from utils.generate import generate_node_message

node = generate_node_message(
    user_id=123456789,
    nickname="发送者昵称",
    content=[generate_text_message("消息内容")]
)
```

---

### generate_file_message

生成文件消息段（自动转换为 Base64）。

```python
from utils.generate import generate_file_message

with open("document.pdf", "rb") as f:
    file_bytes = f.read()

msg = generate_file_message(file_bytes, name="document.pdf")
```

---

### generate_rps_message

生成猜拳消息。

```python
from utils.generate import generate_rps_message

msg = generate_rps_message()
# 返回: {"type": "rps", "data": {}}
```

---

### generate_dice_message

生成骰子消息。

```python
from utils.generate import generate_dice_message

msg = generate_dice_message()
# 返回: {"type": "dice", "data": {}}
```

---

## 开关系统 API

位置：`app/core/switchs.py`

### is_group_switch_on

检查群开关是否开启。

```python
from core.switchs import is_group_switch_on

is_on = is_group_switch_on(group_id, MODULE_NAME)
# 返回: bool
```

---

### is_private_switch_on

检查私聊开关是否开启。

```python
from core.switchs import is_private_switch_on

is_on = is_private_switch_on(MODULE_NAME)
# 返回: bool
```

---

### toggle_group_switch

切换群开关状态。

```python
from core.switchs import toggle_group_switch

new_state = toggle_group_switch(group_id, MODULE_NAME)
# 返回: bool (新状态)
```

---

### toggle_private_switch

切换私聊开关状态。

```python
from core.switchs import toggle_private_switch

new_state = toggle_private_switch(MODULE_NAME)
# 返回: bool (新状态)
```

---

### handle_module_group_switch

处理群开关命令（带消息回复）。

```python
from core.switchs import handle_module_group_switch

await handle_module_group_switch(MODULE_NAME, websocket, group_id, message_id)
```

---

### handle_module_private_switch

处理私聊开关命令（带消息回复）。

```python
from core.switchs import handle_module_private_switch

await handle_module_private_switch(MODULE_NAME, websocket, user_id, message_id)
```

---

### load_group_all_switch

获取某群组所有模块的开关状态。

```python
from core.switchs import load_group_all_switch

switches = load_group_all_switch(group_id)
# 返回: dict {module_name: bool, ...}
```

---

### get_all_enabled_groups

获取某模块所有已开启的群列表。

```python
from core.switchs import get_all_enabled_groups

groups = get_all_enabled_groups(MODULE_NAME)
# 返回: list [group_id, ...]
```

---

### copy_group_switches

复制群组开关设置。

```python
from core.switchs import copy_group_switches

copy_group_switches(source_group_id, target_group_id)
```

---

## 权限认证 API

位置：`app/utils/auth.py`

### is_system_admin

判断是否为系统管理员（OWNER_ID）。

```python
from utils.auth import is_system_admin

if is_system_admin(user_id):
    # 是系统管理员
    pass
```

---

### is_group_admin

判断是否为群管理员或群主。

```python
from utils.auth import is_group_admin

# role 从消息的 sender.role 获取
if is_group_admin(role):
    # 是群管理员或群主
    pass
```

**role 可选值：**

| 值 | 说明 |
|----|------|
| `owner` | 群主 |
| `admin` | 管理员 |
| `member` | 普通成员 |

---

## 组合使用示例

### 发送带回复和 @ 的消息

```python
from api.message import send_group_msg
from utils.generate import (
    generate_reply_message,
    generate_at_message,
    generate_text_message,
)

await send_group_msg(websocket, group_id, [
    generate_reply_message(message_id),
    generate_at_message(user_id),
    generate_text_message(" 你好！欢迎使用本机器人。"),
])
```

### 发送图文消息

```python
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_image_message

await send_group_msg(websocket, group_id, [
    generate_text_message("这是一张图片："),
    generate_image_message("http://example.com/image.png", type="url"),
])
```

### 有权限限制的命令

```python
from utils.auth import is_system_admin, is_group_admin
from api.message import send_group_msg

async def handle_admin_command(websocket, msg):
    user_id = str(msg.get("user_id"))
    group_id = str(msg.get("group_id"))
    role = msg.get("sender", {}).get("role", "")

    # 系统管理员或群管理员才能执行
    if not is_system_admin(user_id) and not is_group_admin(role):
        await send_group_msg(websocket, group_id, "你没有权限执行此命令")
        return

    # 执行管理员命令
    await do_admin_stuff()
```
