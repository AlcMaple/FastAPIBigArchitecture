from loguru import logger
import os
from sys import stdout


def setup_all_loggers(project_root: str = "./"):
    """统一日志配置"""

    # 控制台输出配置
    LOGURU_FORMAT: str = (
        "<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> │ "
        "<level>{level: <8}</level> │ {message}"
    )
    logger.configure(handlers=[{"sink": stdout, "format": LOGURU_FORMAT}])

    # HTTP访问日志配置
    prod_dir = os.path.join(project_root, "log/prod")
    if not os.path.exists(prod_dir):
        os.makedirs(prod_dir, exist_ok=True)

    info_log_path = os.path.join(prod_dir, "info_{time:YYYYMMDD}.log")
    error_log_path = os.path.join(prod_dir, "error_{time:YYYYMMDD}.log")

    # INFO级别日志 (中间件的请求响应日志)
    format2 = " {time:YYYY-MM-DD HH:mm:ss.SSS} | thread_id:{thread.id} thread_name:{thread.name} | {level} | {message}"
    logger.add(
        info_log_path,
        format=format2,
        rotation="00:00",
        encoding="utf-8",
        level="INFO",
        enqueue=True,
    )

    # ERROR级别日志
    format1 = " {time:YYYY-MM-DD HH:mm:ss.SSS} | thread_id:{thread.id} thread_name:{thread.name} | {level} |\n {message}"
    logger.add(
        error_log_path,
        format=format1,
        rotation="00:00",
        encoding="utf-8",
        level="ERROR",
        enqueue=True,
    )

    # 业务逻辑日志配置
    dev_dir = os.path.join(project_root, "log/dev")
    if not os.path.exists(dev_dir):
        os.makedirs(dev_dir, exist_ok=True)

    dev_log_path = os.path.join(dev_dir, "{time:YYYYMMDD}_arch.log")
    dev_format = " {time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    # 检查是否已添加业务日志处理器
    business_handler_exists = False
    for handler in logger._core.handlers.values():
        if hasattr(handler, "_sink") and isinstance(handler._sink, str):
            if "arch.log" in handler._sink:
                business_handler_exists = True
                break

    if not business_handler_exists:
        logger.add(
            dev_log_path,
            format=dev_format,
            rotation="00:00",
            encoding="utf-8",
            level="DEBUG",
            enqueue=True,
        )


async def async_trace_add_log_record(event_type="", msg={}, remarks=""):
    """
    中间件日志写入函数
    """
    try:
        import json

        log_content = {
            "event_type": event_type,
            "data": msg,
            "remarks": remarks,  # 备注信息
            "timestamp": f"{msg.get('ts', '')}" if isinstance(msg, dict) else "",
        }

        if event_type == "request":
            logger.info(
                f"Request Log: {json.dumps(log_content, ensure_ascii=False)}"
            )  # 输出日志不转义，有中文直接输出中文
        elif event_type == "response":
            logger.info(f"Response Log: {json.dumps(log_content, ensure_ascii=False)}")
        elif event_type == "error":
            logger.error(f"Error Log: {json.dumps(log_content, ensure_ascii=False)}")
        else:
            logger.info(f"General Log: {json.dumps(log_content, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"Failed to write log: {str(e)}")
        logger.error(f"Original message: {msg}")


__all__ = ["logger", "setup_all_loggers", "async_trace_add_log_record"]
