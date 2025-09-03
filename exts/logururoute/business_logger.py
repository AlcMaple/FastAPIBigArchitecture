from loguru import logger as _base_logger
import os


def setup_business_logger(log_dev_path: str = None):
    """
    设置业务逻辑日志配置
    用于开发环境的业务逻辑调试日志
    """
    if not log_dev_path:
        # 获取项目根目录路径
        current_file_dir = os.path.split(os.path.realpath(__file__))[
            0
        ]  # exts/logururoute
        exts_dir = os.path.dirname(current_file_dir)  # exts
        log_dev_path = os.path.dirname(exts_dir)  # 项目根目录

    # 检查开发环境日志目录是否存在
    log_dir = os.path.join(log_dev_path, "log/dev")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 定义业务日志文件名称
    dev_log_file_path = os.path.join(log_dir, "{time:YYYYMMDD}_arch.log")

    # 配置日志文件格式
    format_template = " {time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    # 检查是否已经添加了业务日志文件处理器
    business_handler_exists = False
    for handler in _base_logger._core.handlers.values():
        if hasattr(handler, "_sink") and isinstance(handler._sink, str):
            if "arch.log" in handler._sink:
                business_handler_exists = True
                break

    if not business_handler_exists:
        # 添加业务日志文件，包含所有级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        _base_logger.add(
            dev_log_file_path,
            format=format_template,
            rotation="00:00",
            encoding="utf-8",
            level="DEBUG",  # 记录DEBUG及以上级别的所有日志
            enqueue=True,
        )

    return _base_logger


# 初始化业务日志配置并导出
logger = setup_business_logger()
