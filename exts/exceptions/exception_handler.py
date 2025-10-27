"""
全局异常处理器
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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
        2. RequestValidationError - Pydantic 参数校验异常
        3. StarletteHTTPException - HTTP 异常
        4. Exception - 所有未捕获的异常
        """
        # 业务异常（最高优先级）
        app.add_exception_handler(ApiException, self.handle_api_exception)

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

    async def handle_validation_error(
        self, request: Request, exc: RequestValidationError
    ):
        """
        处理 Pydantic 参数校验异常
        """
        logger.error(f"[ValidationError] {request.method} {request.url}")
        logger.error(f"  Errors: {exc.errors()}")

        # 提取第一个错误信息作为主要提示
        errors = exc.errors()
        if errors:
            first_error = errors[0]
            field = " -> ".join(str(loc) for loc in first_error["loc"][1:])
            message = f"参数 '{field}' {first_error['msg']}"
        else:
            message = "参数校验失败"

        return Error(
            code=ErrorCode.PARAMETER_ERROR.code,
            message=message,
            data={"errors": errors, "body": exc.body} if errors else None,
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
