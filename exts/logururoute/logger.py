from loguru import logger
import os
from sys import stdout
import json


def setup_ext_loguru(log_pro_path: str = None):
    if not log_pro_path:
        # 当前日志文件的存储路径
        log_pro_path = os.path.split(os.path.realpath(__file__))[0]

    # 检查日志目录是否存在
    log_dir = os.path.join(log_pro_path, "log/prod")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 定义 info_log 文件名称
    log_file_path = os.path.join(log_dir, "info_{time:YYYYMMDD}.log")
    err_log_file_path = os.path.join(log_dir, "error_{time:YYYYMMDD}.log")

    LOGURU_FORMAT: str = (
        "<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> │ "
        "<level>{level: <8}</level> │ {message}"
    )
    # 指定 loguru 日志处理方式和输出格式
    # handlers：指定日志处理器，列表类型
    # sink:stdout 输出到控制台
    logger.configure(handlers=[{"sink": stdout, "format": LOGURU_FORMAT}])
    # 配置 ERROR 类型日志格式
    format = " {time:YYYY-MM-DD HH:mm:ss.SSS} | thread_id:{thread.id} thread_name:{thread.name} | {level} |\n {message}"
    # rotation：每天0 点进行文件日志切割
    # enqueue：是否异步写入日志文件
    logger.add(
        err_log_file_path,
        format=format,
        rotation="00:00",
        encoding="utf-8",
        level="ERROR",
        enqueue=True,
    )
    # 配置 INFO 类型日志格式
    format2 = " {time:YYYY-MM-DD HH:mm:ss.SSS} | thread_id:{thread.id} thread_name:{thread.name} | {level} | {message}"
    logger.add(
        log_file_path,
        format=format2,
        rotation="00:00",
        encoding="utf-8",
        level="INFO",
        enqueue=True,
    )


async def async_trace_add_log_record(event_type="", msg={}, remarks=""):
    """
    日志写入
    """
    try:
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
