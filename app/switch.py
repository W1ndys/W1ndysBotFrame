# 群组开关

import json

from app.api import *

SWITCH_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app",
    "data",
    "GroupSwitch",
)

logging.info(f"群组开关数据目录: {SWITCH_DATA_DIR}")


# 查看功能开关状态
def load_function_status(group_id):
    return load_switch(group_id, "example")


# 保存功能开关状态
def save_function_status(group_id, status):
    save_switch(group_id, "example", status)


# 加载群组开关
def load_switch(group_id, key):
    try:
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "r", encoding="utf-8"
        ) as f:
            switches = json.load(f)
    except FileNotFoundError:
        # 创建文件并写入空字典
        switches = {}
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(switches, f, ensure_ascii=False, indent=4)

    return switches.get(key, False)


# 保存群组开关
def save_switch(group_id, key, switch):
    try:
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "r", encoding="utf-8"
        ) as f:
            switches = json.load(f)
    except FileNotFoundError:
        switches = {}

    switches[key] = switch

    with open(
        os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(switches, f, ensure_ascii=False, indent=4)


# 获取所有群组的开关状态
def get_all_group_switches():
    all_switches = {}
    for filename in os.listdir(SWITCH_DATA_DIR):
        if filename.endswith(".json"):
            group_id = filename[:-5]  # 移除 '.json' 后缀
            try:
                with open(
                    os.path.join(SWITCH_DATA_DIR, filename), "r", encoding="utf-8"
                ) as f:
                    switches = json.load(f)
                    all_switches[group_id] = switches
            except json.JSONDecodeError:
                logging.error(f"无法解析 {filename} 的开关内容")
            except Exception as e:
                logging.error(f"读取开关 {filename} 时发生错误: {str(e)}")
    return all_switches


# 获取群组所有开关
def GroupSwitch(group_id):
    try:
        os.makedirs(SWITCH_DATA_DIR, exist_ok=True)
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "r", encoding="utf-8"
        ) as f:
            switches = json.load(f)
            return switches
    except FileNotFoundError:
        return None


# 查看群所有状态
async def view_group_status(websocket, group_id, raw_message, message_id):
    if raw_message == "groupswitch":
        group_status = GroupSwitch(group_id)

        if group_status:
            status_message = f"[CQ:reply,id={message_id}]群 {group_id} 的状态:\n\n"
            for key, value in group_status.items():
                status_message += f"{key}: {value}\n"
            # 删除最后一个换行符
            # 把true和false转换为开和关
            status_message = status_message.replace("True", "开").replace("False", "关")
            status_message = status_message.rstrip("\n")
        else:
            status_message = (
                f"[CQ:reply,id={message_id}]未找到群 {group_id} 的状态信息。"
            )

        await send_group_msg(websocket, group_id, status_message)


# 处理群消息
async def handle_GroupSwitch_group_message(websocket, msg):

    # 确保数据目录存在
    os.makedirs(SWITCH_DATA_DIR, exist_ok=True)

    group_id = msg["group_id"]
    raw_message = msg["raw_message"]
    message_id = int(msg["message_id"])

    await view_group_status(websocket, group_id, raw_message, message_id)


# 统一事件处理入口
async def handle_events(websocket, msg):
    """统一事件处理入口"""
    post_type = msg.get("post_type", "response")  # 添加默认值
    try:
        # 确保数据目录存在
        os.makedirs(SWITCH_DATA_DIR, exist_ok=True)

        # 处理回调事件
        if msg.get("status") == "ok":
            pass
            return

        post_type = msg.get("post_type")

        # 处理元事件
        if post_type == "meta_event":
            pass

        # 处理消息事件
        elif post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await handle_GroupSwitch_group_message(websocket, msg)
            elif message_type == "private":
                return

        # 处理通知事件
        elif post_type == "notice":
            if msg.get("notice_type") == "group":
                load_switch(msg.get("group_id"), "GroupEntryVerification")

    except Exception as e:
        error_type = {
            "message": "消息",
            "notice": "通知",
            "request": "请求",
            "meta_event": "元事件",
        }.get(post_type, "未知")

        logging.error(f"处理GroupSwitch{error_type}事件失败: {e}")

        # 发送错误提示
        if post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await send_group_msg(
                    websocket,
                    msg.get("group_id"),
                    f"处理GroupSwitch{error_type}事件失败，错误信息：{str(e)}",
                )
            elif message_type == "private":
                await send_private_msg(
                    websocket,
                    msg.get("user_id"),
                    f"处理GroupSwitch{error_type}事件失败，错误信息：{str(e)}",
                )
