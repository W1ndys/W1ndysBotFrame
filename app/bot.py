# bot.py

import logging
import asyncio
import websockets
from config import *


from handler_events import handle_message

from api import send_private_msg


async def connect_to_bot():
    logging.info("正在连接到机器人...")

    # 如果 token 不为 None，则在 URL 中添加 token 参数
    connection_url = ws_url
    if token is not None:
        # 检查 URL 是否已经包含参数
        if "?" in ws_url:
            connection_url = f"{ws_url}&access_token={token}"
        else:
            connection_url = f"{ws_url}?access_token={token}"

    logging.info(f"连接地址: {connection_url}")

    # 连接到 WebSocket
    async with websockets.connect(connection_url) as websocket:
        try:
            async for message in websocket:
                try:
                    # 直接处理消息
                    await handle_message(websocket, message)
                except Exception as e:
                    # 添加更详细的错误日志
                    logging.error(f"处理消息时出错: {e}")
                    logging.error(f"消息内容: {message}")
                    # 可选：将错误通知发送给机器人所有者
                    try:
                        await send_private_msg(
                            websocket,
                            owner_id[0],
                            f"处理消息时出错: {e}\n消息内容: {message}",
                        )
                    except Exception as notify_error:
                        logging.error(f"发送错误通知失败: {notify_error}")
        except Exception as e:
            logging.error(f"WebSocket连接出错: {e}")
            raise
