from loguru import logger
from sys import stdout
import os

from config.settings import settings


def setup_business_logger(log_path: str = None):
    """
    业务日志配置
    """
    # 测试环境，不配置日志
    if os.environ.get("TESTING") == "true":
        return logger

    # 移除默认的 logger，避免重复输出
    logger.remove()

    # 控制台输出配置
    console_format = (
        "<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> │ "
        "<level>{level: <8}</level> │ "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> │ {message}"
    )

    # 添加控制台输出处理器
    logger.add(
        stdout,
        format=console_format,
        level="DEBUG",
        enqueue=True,
    )

    # if not log_path:
    #     # 获取项目根目录路径
    #     current_file_dir = os.path.split(os.path.realpath(__file__))[0]
    #     exts_dir = os.path.dirname(current_file_dir)
    #     log_path = os.path.dirname(exts_dir)

    # 确保日志目录存在
    log_dir = settings.log_dir
    # log_dir = os.path.join(log_path, "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 日志文件路径: log/YYYYMMDD.log
    log_file_path = os.path.join(log_dir, "{time:YYYYMMDD}.log")

    # 文件日志格式
    file_format = " {time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    # 添加文件日志处理器
    logger.add(
        log_file_path,
        format=file_format,
        rotation="00:00",  # 每天凌晨0点切分日志
        encoding="utf-8",
        level="DEBUG",
        enqueue=True,
    )

    return logger


# 初始化业务日志
logger = setup_business_logger()
