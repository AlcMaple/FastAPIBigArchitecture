from loguru import logger
import os


def setup_business_logger(log_dev_path: str = None):
    """
    设置业务逻辑日志配置
    用于开发环境的业务逻辑调试日志
    """
    # 测试环境，不配置日志
    if os.environ.get("TESTING") == "true":
        return logger

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

    # 配置业务日志文件格式
    file_format = " {time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    # 添加业务日志文件处理器
    logger.add(
        dev_log_file_path,
        format=file_format,
        rotation="00:00",
        encoding="utf-8",
        level="DEBUG",  # 记录DEBUG及以上级别的所有日志
        enqueue=True,
        filter=lambda record: (
            # 记录业务日志或者没有middleware标记的日志（默认业务日志）
            "business" in record.get("extra", {})
            or "middleware" not in record.get("extra", {})
        ),
    )

    return logger


# 初始化业务日志并绑定business标记
_business_logger = setup_business_logger()
logger = _business_logger.bind(business=True)
