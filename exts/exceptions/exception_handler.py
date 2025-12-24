"""
全局异常处理器
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DBAPIError

from .api_exception import ApiException
from .error_code import ErrorCode
from exts.responses.api_response import Error
from exts.logururoute.business_logger import logger


class GlobalExceptionHandler:
    """全局异常处理器"""

    def __init__(self, app: FastAPI = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: FastAPI):
        """
        注册异常处理器到 FastAPI 应用

        处理优先级（从高到低）：
        1. ApiException - 业务异常（开发者主动抛出）
        2. IntegrityError - 数据库完整性错误（唯一键、外键冲突等）
        3. SQLAlchemyError - 数据库操作错误
        4. RequestValidationError - Pydantic 参数校验异常
        5. StarletteHTTPException - HTTP 异常
        6. Exception - 所有未捕获的异常
        """
        # 业务异常（最高优先级）
        app.add_exception_handler(ApiException, self.handle_api_exception)

        # 数据库完整性异常（唯一键、外键冲突等）
        app.add_exception_handler(IntegrityError, self.handle_integrity_error)

        # 数据库操作异常
        app.add_exception_handler(SQLAlchemyError, self.handle_database_error)

        # 参数校验异常
        app.add_exception_handler(RequestValidationError, self.handle_validation_error)

        # HTTP 异常
        app.add_exception_handler(StarletteHTTPException, self.handle_http_exception)

        # 兜底异常处理
        app.add_exception_handler(Exception, self.handle_unexpected_exception)

    async def handle_api_exception(self, request: Request, exc: ApiException):
        """
        处理业务异常（ApiException）
        """
        logger.warning(f"[BizError] {request.method} {request.url} ")
        logger.warning(f"  Error Code: {exc.code} ")
        logger.warning(f"  Message: {exc.message} ")

        return Error(
            code=exc.code,
            message=exc.message,
            data=exc.data,
            http_status=exc.http_status,
        )

    async def handle_integrity_error(self, request: Request, exc: IntegrityError):
        """
        处理数据库完整性错误（唯一键冲突、外键约束等）
        """
        logger.error(f"[IntegrityError] {request.method} {request.url}")
        logger.error(f"  Error: {str(exc)}")

        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        error_lower = error_msg.lower()

        # 默认错误
        target_error = ErrorCode.DATABASE_ERROR

        # 判断具体的完整性错误类型
        if "duplicate" in error_lower or "unique" in error_lower:
            target_error = ErrorCode.DUPLICATE_KEY_ERROR
        elif "foreign key" in error_lower:
            target_error = ErrorCode.FOREIGN_KEY_ERROR

        return Error(
            code=target_error.code,
            message=target_error.message,
            # 在开发环境返回详细信息，生产环境去掉 detail_msg
            data={"detail": error_msg} if error_msg else None,
            http_status=target_error.http_status,
        )

    async def handle_database_error(self, request: Request, exc: SQLAlchemyError):
        """
        处理数据库操作错误（连接失败、SQL 语法错误等）
        """
        logger.error(f"[DatabaseError] {request.method} {request.url}")
        logger.error(f"  Error Type: {type(exc).__name__}")
        logger.error(f"  Error: {str(exc)}")

        target_error = ErrorCode.DATABASE_ERROR

        # 判断是否为连接错误
        error_str = str(exc).lower()
        if isinstance(exc, DBAPIError) and (
            "connect" in error_str or "connection" in error_str
        ):
            target_error = ErrorCode.DATABASE_CONNECTION_ERROR

        return Error(
            code=target_error.code,
            message=target_error.message,
            http_status=target_error.http_status,
        )

    async def handle_validation_error(
        self, request: Request, exc: RequestValidationError
    ):
        """
        处理 Pydantic 参数校验异常
        """
        logger.warning(f"[ParamError] {request.method} {request.url}")
        logger.warning(f"  Errors: {exc.errors()}")

        # 获取原始错误列表
        errors = exc.errors()
        target_error = ErrorCode.VALIDATION_ERROR
        message = target_error.message

        # 错误提示
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

        # 可序列化错误数据
        serializable_errors = jsonable_encoder(errors)

        return Error(
            code=ErrorCode.PARAMETER_ERROR.code,
            message=message,
            data={"errors": serializable_errors},
            http_status=ErrorCode.PARAMETER_ERROR.http_status,
        )

    async def handle_http_exception(
        self, request: Request, exc: StarletteHTTPException
    ):
        """
        处理 HTTP 异常
        """
        logger.error(f"[HTTPException] {request.method} {request.url}")
        logger.error(f"  Status Code: {exc.status_code}")
        logger.error(f"  Detail: {exc.detail}")

        # HTTP 状态码映射到错误码
        status_code_map = {
            400: ErrorCode.BAD_REQUEST,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            405: ErrorCode.METHOD_NOT_ALLOWED,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_SERVER_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }

        error_code = status_code_map.get(
            exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR
        )

        return Error(
            code=error_code.code,
            message=str(exc.detail) if exc.detail else error_code.message,
            http_status=exc.status_code,
        )

    async def handle_unexpected_exception(self, request: Request, exc: Exception):
        """
        处理所有未捕获的异常
        """
        import traceback

        error_trace = traceback.format_exc()

        logger.error(f"[UnexpectedException] {request.method} {request.url}")
        logger.error(f"  Exception Type: {type(exc).__name__}")
        logger.error(f"  Exception Message: {str(exc)}")
        logger.error(f"  Traceback:\n{error_trace}")

        # 生产环境不暴露详细错误信息
        return Error(
            code=ErrorCode.INTERNAL_SERVER_ERROR.code,
            message=ErrorCode.INTERNAL_SERVER_ERROR.message,
            http_status=500,
        )
