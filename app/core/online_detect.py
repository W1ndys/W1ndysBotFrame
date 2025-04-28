# script/example/main.py

import logging
import os
import sys
import asyncio

from app.core.feishu import feishu
from app.core.dingtalk import dingtalk
import time

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import *
from app.api import send_group_msg, send_private_msg
from app.switch import load_switch, save_switch


# 数据存储路径，实际开发时，请将Example替换为具体的数据存放路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "Example",
)


# 查看功能开关状态
def load_function_status(group_id):
    return load_switch(group_id, "Example")


# 保存功能开关状态
def save_function_status(group_id, status):
    save_switch(group_id, "Example", status)


# 处理开关状态
async def toggle_function_status(websocket, group_id, message_id, authorized):
    if not authorized:
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]❌❌❌你没有权限对Example功能进行操作,请联系管理员。",
        )
        return

    if load_function_status(group_id):
        save_function_status(group_id, False)
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]🚫🚫🚫Example功能已关闭",
        )
    else:
        save_function_status(group_id, True)
        await send_group_msg(
            websocket, group_id, f"[CQ:reply,id={message_id}]✅✅✅Example功能已开启"
        )


# 群消息处理函数
async def handle_group_message(websocket, msg):
    """处理群消息"""
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        message_id = str(msg.get("message_id"))
        authorized = user_id in owner_id

        # 处理开关命令
        if raw_message == "example":
            await toggle_function_status(websocket, group_id, message_id, authorized)
            return
        # 检查功能是否开启
        if load_function_status(group_id):
            # 其他群消息处理逻辑
            pass
    except Exception as e:
        logging.error(f"处理Example群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            "处理Example群消息失败，错误信息：" + str(e),
        )
        return


# 私聊消息处理函数
async def handle_private_message(websocket, msg):
    """处理私聊消息"""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        user_id = str(msg.get("user_id"))
        raw_message = str(msg.get("raw_message"))
        # 私聊消息处理逻辑
        pass
    except Exception as e:
        logging.error(f"处理Example私聊消息失败: {e}")
        await send_private_msg(
            websocket,
            msg.get("user_id"),
            "处理Example私聊消息失败，错误信息：" + str(e),
        )
        return


# 群通知处理函数
async def handle_group_notice(websocket, msg):
    """处理群通知"""
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        notice_type = str(msg.get("notice_type"))
        operator_id = str(msg.get("operator_id", ""))

    except Exception as e:
        logging.error(f"处理Example群通知失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            "处理Example群通知失败，错误信息：" + str(e),
        )
        return


# 回应事件处理函数
async def handle_response(websocket, msg):
    """处理回调事件"""
    try:
        echo = msg.get("echo")
        if echo and echo.startswith("xxx"):
            # 回调处理逻辑
            pass
    except Exception as e:
        logging.error(f"处理Example回调事件失败: {e}")
        await send_group_msg(
            websocket,
            msg.get("group_id"),
            f"处理Example回调事件失败，错误信息：{str(e)}",
        )
        return


# 请求事件处理函数
async def handle_request_event(websocket, msg):
    """处理请求事件"""
    try:
        request_type = msg.get("request_type")
        pass
    except Exception as e:
        logging.error(f"处理Example请求事件失败: {e}")
        return


class OnlineDetectManager:
    def __init__(self):
        self.is_online = True  # 初始状态为在线
        self.last_state_change_time = 0
        self.last_report_time = 0
        # 状态变化的最小时间间隔(秒)，防止频繁上报
        self.min_report_interval = 60
        self.owner_id = owner_id

    async def handle_events(self, websocket, message):
        """处理元事件，包括首次连接和心跳事件"""
        # 处理首次连接事件
        if (
            message.get("post_type") == "meta_event"
            and message.get("meta_event_type") == "lifecycle"
            and message.get("sub_type") == "connect"
        ):
            current_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(message.get("time", int(time.time()))),
            )
            connect_msg = f"W1ndysBot已上线！\n机器人ID: {message.get('self_id')}\n上线时间: {current_time}"
            logging.info(f"机器人首次连接: {connect_msg}")

            # 向所有管理员发送私聊消息
            try:
                tasks = [
                    send_private_msg(websocket, owner, connect_msg)
                    for owner in self.owner_id
                ]
                await asyncio.gather(*tasks)
            except Exception as e:
                logging.error(f"发送上线通知失败: {e}")
            return

        # 处理心跳事件
        if (
            message.get("post_type") == "meta_event"
            and message.get("meta_event_type") == "heartbeat"
        ):
            await self.handle_heartbeat(websocket, message)

    async def handle_heartbeat(self, websocket, message):
        """处理心跳事件，检测在线状态"""
        # 获取在线状态
        status = message.get("status", {})
        current_online = status.get("online", False)

        # 如果是首次检测或状态发生变化
        current_time = int(time.time())
        if self.is_online is None or self.is_online != current_online:
            # 检查是否达到最小上报间隔
            if current_time - self.last_report_time >= self.min_report_interval:
                self.last_state_change_time = current_time
                self.last_report_time = current_time

                # 生成通知消息
                if self.is_online is None:
                    status_text = "初始化" if current_online else "掉线"
                else:
                    status_text = "重新上线" if current_online else "掉线"

                title = f"机器人状态变更: {status_text}"
                content = (
                    f"机器人ID: {message.get('self_id')}\n"
                    f"当前状态: {'在线' if current_online else '离线'}\n"
                    f"状态变更时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}\n"
                    f"心跳间隔: {message.get('interval', 0)/1000}秒"
                )

                # 发送通知
                logging.info(f"机器人状态变更: {status_text}")
                try:
                    # 发送飞书通知
                    feishu_result = feishu(title, content)
                    if "error" in feishu_result:
                        logging.error(f"发送飞书通知失败: {feishu_result.get('error')}")

                    # 发送钉钉通知
                    dingtalk(title, content)
                except Exception as e:
                    logging.error(f"发送通知失败: {e}")

            # 更新状态
            self.is_online = current_online


# 创建全局实例
Online_detect_manager = OnlineDetectManager()


# 统一事件处理入口
async def handle_events(websocket, msg):
    """统一事件处理入口"""
    post_type = msg.get("post_type", "response")  # 添加默认值
    try:
        # 这里可以放一些定时任务，在函数内设置时间差检测即可

        # 处理回调事件，用于一些需要获取ws返回内容的事件
        if msg.get("status") == "ok":
            await handle_response(websocket, msg)
            return

        post_type = msg.get("post_type")

        # 处理元事件，每次心跳时触发，用于一些定时任务
        if post_type == "meta_event":
            await Online_detect_manager.handle_events(websocket, msg)

        # 处理消息事件，用于处理群消息和私聊消息
        elif post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await handle_group_message(websocket, msg)
            elif message_type == "private":
                await handle_private_message(websocket, msg)

        # 处理通知事件，用于处理群通知
        elif post_type == "notice":
            await handle_group_notice(websocket, msg)

        # 处理请求事件，用于处理请求事件
        elif post_type == "request":
            await handle_request_event(websocket, msg)

    except Exception as e:
        error_type = {
            "message": "消息",
            "notice": "通知",
            "request": "请求",
            "meta_event": "元事件",
        }.get(post_type, "未知")

        logging.error(f"处理Example{error_type}事件失败: {e}")

        # 发送错误提示
        if post_type == "message":
            message_type = msg.get("message_type")
            if message_type == "group":
                await send_group_msg(
                    websocket,
                    msg.get("group_id"),
                    f"处理Example{error_type}事件失败，错误信息：{str(e)}",
                )
            elif message_type == "private":
                await send_private_msg(
                    websocket,
                    msg.get("user_id"),
                    f"处理Example{error_type}事件失败，错误信息：{str(e)}",
                )
