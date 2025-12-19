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
        处理业务异常（ApiException）,抛出的异常，直接转换为 Error 响应
        """
        logger.error(f"[ApiException] {request.method} {request.url}")
        logger.error(f"  Error Code: {exc.code}")
        logger.error(f"  Message: {exc.message}")
        if exc.data:
            logger.error(f"  Data: {exc.data}")

        return Error(
            code=exc.code,
            message=exc.message,
            data=exc.data,
        )

    async def handle_integrity_error(self, request: Request, exc: IntegrityError):
        """
        处理数据库完整性错误（唯一键冲突、外键约束等）
        """
        logger.error(f"[IntegrityError] {request.method} {request.url}")
        logger.error(f"  Error: {str(exc)}")

        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)

        # 判断具体的完整性错误类型
        if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
            # 唯一键冲突
            return Error(
                code=ErrorCode.DUPLICATE_KEY_ERROR.code,
                message="数据重复，违反唯一性约束",
                data={"detail": error_msg} if error_msg else None,
            )
        elif "foreign key" in error_msg.lower():
            # 外键约束错误
            return Error(
                code=ErrorCode.FOREIGN_KEY_ERROR.code,
                message="外键约束错误，关联数据不存在或被引用",
                data={"detail": error_msg} if error_msg else None,
            )
        else:
            # 其他完整性错误
            return Error(
                code=ErrorCode.DATABASE_ERROR.code,
                message="数据库完整性约束错误",
                data={"detail": error_msg} if error_msg else None,
            )

    async def handle_database_error(self, request: Request, exc: SQLAlchemyError):
        """
        处理数据库操作错误（连接失败、SQL 语法错误等）
        """
        logger.error(f"[DatabaseError] {request.method} {request.url}")
        logger.error(f"  Error Type: {type(exc).__name__}")
        logger.error(f"  Error: {str(exc)}")

        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)

        # 判断是否为连接错误
        if isinstance(exc, DBAPIError) and "connect" in error_msg.lower():
            return Error(
                code=ErrorCode.DATABASE_CONNECTION_ERROR.code,
                message="数据库连接失败，请稍后重试",
            )

        # 其他数据库错误
        return Error(
            code=ErrorCode.DATABASE_ERROR.code,
            message="数据库操作异常",
            data={"error_type": type(exc).__name__} if error_msg else None,
        )

    async def handle_validation_error(
        self, request: Request, exc: RequestValidationError
    ):
        """
        处理 Pydantic 参数校验异常
        """
        logger.error(f"[ValidationError] {request.method} {request.url}")
        logger.error(f"  Errors: {exc.errors()}")

        # 获取原始错误列表
        errors = exc.errors()

        # 提取第一个错误信息作为主要提示
        if errors:
            first_error = errors[0]
            field = " -> ".join(str(loc) for loc in first_error["loc"][1:])
            message = f"参数 '{field}' {first_error['msg']}"
        else:
            message = "参数校验失败"

        cleaned_errors = []
        for error in errors:
            cleaned_error = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
            }
            if "url" in error:
                cleaned_error["url"] = error["url"]
            cleaned_errors.append(cleaned_error)

        # 可序列化错误数据
        serializable_errors = jsonable_encoder(cleaned_errors)

        return Error(
            code=ErrorCode.PARAMETER_ERROR.code,
            message=message,
            data={"errors": serializable_errors} if serializable_errors else None,
            http_status=422,
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
