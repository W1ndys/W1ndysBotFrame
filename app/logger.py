# logger.py

import logging
import colorlog
import os
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler


def setup_logger(name=None, log_file=None, level=logging.INFO):
    """
    设置日志记录器

    Args:
        name: 日志记录器名称，如果为None则获取root logger
        log_file: 日志文件路径，如果为None则自动生成
        level: 日志级别，默认为DEBUG

    Returns:
        配置好的logger对象
    """
    # 获取logger
    logger = logging.getLogger(name)

    # 清除之前的处理器
    logger.handlers = []

    # 创建并配置控制台彩色处理器
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s %(levelname)s:%(name)s:%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "light_green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    # 确定日志文件路径
    if log_file is None:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(current_dir, "logs")

        # 创建 logs 目录
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # 以当前启动时间为文件名，使用东八区时间
        tz = timezone(timedelta(hours=8))
        log_filename = os.path.join(
            logs_dir, datetime.now(tz).strftime("%Y-%m-%d_%H-%M-%S.log")
        )
    else:
        log_filename = log_file
        log_dir = os.path.dirname(log_filename)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    # 添加 RotatingFileHandler 将日志保存到本地文件，并在超过1MB时新建文件
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s:%(name)s:%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # 自定义轮转日志文件命名
    tz = timezone(timedelta(hours=8))
    file_handler.namer = lambda name: name.replace(
        ".log", f"_{datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )
    file_handler.rotator = lambda source, dest: os.rename(source, dest)

    # 设置日志记录器的级别和处理器
    logger.setLevel(level)
    console_handler.setLevel(level)
    file_handler.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # 确保日志及时刷新
    for handler in logger.handlers:
        handler.flush()

    logger.info("初始化日志器")
    logger.info(f"日志文件名: {log_filename}")

    return logger


# 创建默认logger
logger = setup_logger()


def info(msg):
    """记录信息日志"""
    logger.info(msg)


def warning(msg):
    """记录警告日志"""
    logger.warning(msg)


def error(msg):
    """记录错误日志"""
    logger.error(msg)


def debug(msg):
    """记录调试日志"""
    logger.debug(msg)


def critical(msg):
    """记录严重错误日志"""
    logger.critical(msg)
