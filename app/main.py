# main.py

import asyncio
from bot import connect_to_bot
import logger
import datetime
from logger import setup_logger
from dotenv import load_dotenv

setup_logger()

# 加载环境变量
load_dotenv()


async def main():
    while True:
        try:
            result = await connect_to_bot()
            if result is None:
                raise ValueError("连接返回None")
        except Exception as e:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.error(f"连接失败，正在重试: {e} 当前时间: {current_time}")

            await asyncio.sleep(1)  # 每秒重试一次


if __name__ == "__main__":
    asyncio.run(main())
