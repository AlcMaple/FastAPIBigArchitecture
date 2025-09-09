from loguru import logger as _http_logger
import os
from sys import stdout
import json


def setup_loggers(project_root: str = "./"):
    """HTTP中间件日志"""
    # 测试环境，不配置日志
    if os.environ.get("TESTING") == "true":
        return

    # 控制台输出配置
    LOGURU_FORMAT: str = (
        "<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> │ "
        "<level>{level: <8}</level> │ {message}"
    )
    _http_logger.configure(handlers=[{"sink": stdout, "format": LOGURU_FORMAT}])

    # HTTP访问日志配置
    prod_dir = os.path.join(project_root, "log/prod")
    if not os.path.exists(prod_dir):
        os.makedirs(prod_dir, exist_ok=True)

    info_log_path = os.path.join(prod_dir, "info_{time:YYYYMMDD}.log")
    error_log_path = os.path.join(prod_dir, "error_{time:YYYYMMDD}.log")

    # INFO级别日志
    format2 = " {time:YYYY-MM-DD HH:mm:ss.SSS} | thread_id:{thread.id} thread_name:{thread.name} | {level} | {message}"
    _http_logger.add(
        info_log_path,
        format=format2,
        rotation="00:00",
        encoding="utf-8",
        level="INFO",
        enqueue=True,
    )

    # ERROR级别日志
    format1 = " {time:YYYY-MM-DD HH:mm:ss.SSS} | thread_id:{thread.id} thread_name:{thread.name} | {level} |\n {message}"
    _http_logger.add(
        error_log_path,
        format=format1,
        rotation="00:00",
        encoding="utf-8",
        level="ERROR",
        enqueue=True,
    )


async def async_trace_add_log_record(event_type="", msg={}, remarks=""):
    """
    中间件日志写入函数
    """
    # 测试环境，不记录日志
    if os.environ.get("TESTING") == "true":
        return
    try:
        log_content = {
            "event_type": event_type,
            "data": msg,
            "remarks": remarks,  # 备注信息
            "timestamp": f"{msg.get('ts', '')}" if isinstance(msg, dict) else "",
        }

        if event_type == "request":
            _http_logger.info(
                f"Request Log: {json.dumps(log_content, ensure_ascii=False)}"
            )  # 输出日志不转义，有中文直接输出中文
        elif event_type == "response":
            _http_logger.info(
                f"Response Log: {json.dumps(log_content, ensure_ascii=False)}"
            )
        elif event_type == "error":
            _http_logger.error(
                f"Error Log: {json.dumps(log_content, ensure_ascii=False)}"
            )
        else:
            _http_logger.info(
                f"General Log: {json.dumps(log_content, ensure_ascii=False)}"
            )
    except Exception as e:
        _http_logger.error(f"Failed to write log: {str(e)}")
        _http_logger.error(f"Original message: {msg}")


__all__ = ["setup_loggers", "async_trace_add_log_record"]
