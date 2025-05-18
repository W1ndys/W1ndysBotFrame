# bot.py

import logging
import asyncio
import websockets
from config import *


from handler_events import handle_message

from api import send_private_msg


async def connect_to_bot():
    # 创建消息队列
    message_queue = asyncio.Queue()
    # 用于存储任务的集合
    tasks = set()

    # 消息处理器 - 从队列获取消息并依次处理
    async def message_processor(websocket):
        while True:
            # 从队列中获取消息
            message = await message_queue.get()
            try:
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
            finally:
                # 标记任务完成
                message_queue.task_done()

    # 清理已完成的任务
    def clean_tasks(tasks):
        done = {t for t in tasks if t.done()}
        tasks.difference_update(done)
        for t in done:
            try:
                t.result()
            except Exception as e:
                # 添加更详细的错误日志
                logging.error(f"任务执行出错: {e}")
                logging.exception("详细错误信息:")

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
        # 启动消息处理器
        processor_task = asyncio.create_task(message_processor(websocket))
        tasks.add(processor_task)

        try:
            async for message in websocket:
                # 清理已完成的任务
                clean_tasks(tasks)
                # 将消息放入队列
                await message_queue.put(message)
                logging.debug(f"消息已加入队列，当前队列长度: {message_queue.qsize()}")
        except Exception as e:
            logging.error(f"WebSocket连接出错: {e}")
            raise
        finally:
            # 取消消息处理器任务
            if not processor_task.done():
                processor_task.cancel()
                try:
                    await processor_task
                except asyncio.CancelledError:
                    pass
