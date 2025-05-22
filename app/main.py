import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from logger import logger
from bot import connect_to_bot
from config import *

# 加载.env文件中的环境变量
load_dotenv()


def verify_config():
    """验证配置是否正确"""
    if not OWNER_ID:
        logger.error("OWNER_ID未设置，请在config.py中设置")
        exit()
    if not WS_URL:
        logger.error("WS_URL未设置，请在config.py中设置")
        exit()
    if not TOKEN:
        logger.warning(
            "TOKEN未设置，如果需要使用token认证，请在config.py中设置，若不需要则可以忽略"
        )
    # 以下是选填项
    if not FEISHU_BOT_URL:
        logger.warning(
            "FEISHU_BOT_URL未设置, 飞书机器人可能无法正常工作，若不需要则可以忽略"
        )
    if not FEISHU_BOT_SECRET:
        logger.warning(
            "FEISHU_BOT_SECRET未设置, 飞书机器人可能无法正常工作，若不需要则可以忽略"
        )


class Application:
    def __init__(self):

        # 验证环境变量
        verify_config()

    async def run(self):
        """运行主程序"""
        # 打印当前运行根目录
        logger.info(f"当前运行根目录: {os.getcwd()}")
        while True:
            try:
                result = await connect_to_bot()
                if result is None:
                    raise ValueError("连接返回None")
            except Exception as e:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.error(f"连接失败，正在重试: {e} 当前时间: {current_time}")

                await asyncio.sleep(2)  # 每2秒重试一次


if __name__ == "__main__":

    app = Application()
    asyncio.run(app.run())
