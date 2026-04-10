from loguru import logger
from sys import stdout
import os

from config.settings import settings


def _setup_logger():
    """配置 Loguru 日志：彩色控制台 + 按日切分文件"""
    # 测试环境不配置，避免干扰测试输出
    if os.environ.get("TESTING") == "true":
        return logger

    # 移除默认 handler，避免重复输出
    logger.remove()

    # 控制台：彩色格式
    logger.add(
        stdout,
        format=(
            "<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> │ "
            "<level>{level: <8}</level> │ "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> │ {message}"
        ),
        level="DEBUG",
        enqueue=True,
    )

    # 文件：按天切分，UTF-8
    log_dir = settings.log_dir
    os.makedirs(log_dir, exist_ok=True)
    logger.add(
        os.path.join(log_dir, "{time:YYYYMMDD}.log"),
        format=" {time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        rotation="00:00",
        encoding="utf-8",
        level="DEBUG",
        enqueue=True,
    )

    return logger


logger = _setup_logger()
