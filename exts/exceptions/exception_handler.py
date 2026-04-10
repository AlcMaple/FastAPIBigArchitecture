"""
全局异常处理器
"""

import time
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DBAPIError

from exts.logururoute.business_logger import logger


def _error_response(status_code: int, message: str, data=None) -> JSONResponse:
    """统一构造错误响应"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "code": status_code,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        },
    )


class GlobalExceptionHandler:
    """全局异常处理器"""

    def __init__(self, app: FastAPI = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: FastAPI):
        """
        注册异常处理器到 FastAPI 应用

        处理优先级（从高到低）：
        1. IntegrityError - 数据库完整性错误（唯一键、外键冲突等）
        2. SQLAlchemyError - 数据库操作错误
        3. RequestValidationError - Pydantic 参数校验异常
        4. StarletteHTTPException - HTTP 异常（含业务 raise HTTPException）
        5. Exception - 所有未捕获的异常
        """
        app.add_exception_handler(IntegrityError, self.handle_integrity_error)
        app.add_exception_handler(SQLAlchemyError, self.handle_database_error)
        app.add_exception_handler(RequestValidationError, self.handle_validation_error)
        app.add_exception_handler(StarletteHTTPException, self.handle_http_exception)
        app.add_exception_handler(Exception, self.handle_unexpected_exception)

    async def handle_integrity_error(self, request: Request, exc: IntegrityError):
        """处理数据库完整性错误（唯一键冲突、外键约束等）"""
        logger.error(f"[IntegrityError] {request.method} {request.url}")
        logger.error(f"  Error: {str(exc)}")

        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        error_lower = error_msg.lower()

        if "duplicate" in error_lower or "unique" in error_lower:
            return _error_response(409, "数据已存在，违反唯一性约束")
        elif "foreign key" in error_lower:
            return _error_response(400, "外键约束错误")
        return _error_response(500, "数据库操作异常")

    async def handle_database_error(self, request: Request, exc: SQLAlchemyError):
        """处理数据库操作错误（连接失败、SQL 语法错误等）"""
        logger.error(f"[DatabaseError] {request.method} {request.url}")
        logger.error(f"  Error Type: {type(exc).__name__}")
        logger.error(f"  Error: {str(exc)}")

        error_str = str(exc).lower()
        if isinstance(exc, DBAPIError) and ("connect" in error_str or "connection" in error_str):
            return _error_response(500, "数据库连接失败")
        return _error_response(500, "数据库操作异常")

    async def handle_validation_error(self, request: Request, exc: RequestValidationError):
        """处理 Pydantic 参数校验异常"""
        logger.warning(f"[ParamError] {request.method} {request.url}")
        logger.warning(f"  Errors: {exc.errors()}")

        errors = exc.errors()
        message = "请求参数验证失败"

        if errors:
            first_error = errors[0]
            loc_parts = [
                str(x)
                for x in first_error.get("loc", [])
                if x not in ("body", "query", "path")
            ]
            field_name = ".".join(loc_parts)
            msg = first_error.get("msg", "")
            if field_name:
                message = f"参数 '{field_name}' {msg}"
            else:
                message = msg

        return _error_response(400, message, data={"errors": errors})

    async def handle_http_exception(self, request: Request, exc: StarletteHTTPException):
        """处理 HTTP 异常（含业务逻辑中 raise HTTPException）"""
        logger.warning(f"[HTTPException] {request.method} {request.url}")
        logger.warning(f"  Status Code: {exc.status_code}")
        logger.warning(f"  Detail: {exc.detail}")

        message = str(exc.detail) if exc.detail else "请求错误"
        return _error_response(exc.status_code, message)

    async def handle_unexpected_exception(self, request: Request, exc: Exception):
        """处理所有未捕获的异常"""
        import traceback
        error_trace = traceback.format_exc()

        logger.error(f"[UnexpectedException] {request.method} {request.url}")
        logger.error(f"  Exception Type: {type(exc).__name__}")
        logger.error(f"  Exception Message: {str(exc)}")
        logger.error(f"  Traceback:\n{error_trace}")

        return _error_response(500, "系统内部错误，请联系管理员")
