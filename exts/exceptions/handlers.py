from fastapi import FastAPI, Request, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from enum import Enum
import traceback

from exts.responses.json_response import (
    InternalServerErrorException,
    MethodnotallowedException,
    NotFoundException,
    LimiterResException,
    BadrequestException,
    ParameterException,
    Businesserror,
    Fail,
)
from exts.logururoute.business_logger import logger


class ExceptionEnum(Enum):
    """自定义错误类型枚举类"""

    SUCCESS = ("0000", "OK")
    PARAMETER_ERROR = ("10001", "参数处理异常/错误")
    FAILED = ("5000", "系统异常")
    USER_NO_DATA = ("10001", "用户不存在")
    USER_REGIESTER_ERROR = ("10002", "注册异常")
    PERMISSIONS_ERROR = ("2000", "用户权限错误")


class BusinessError(Exception):
    """自定义业务异常类，根据自定义错误类型枚举类定义来匹配抛出的错误"""

    __slots__ = ["err_code", "err_code_des"]

    def __init__(
        self,
        result: ExceptionEnum = None,
        err_code: str = "0000",
        err_code_des: str = "",
    ):
        if result:
            self.err_code = result.value[0]
            self.err_code_des = err_code_des or result.value[1]
        else:
            self.err_code = err_code
            self.err_code_des = err_code_des
        super().__init__(self)


"""
该框架的插件设计参考了：插件模板（FastAPI 支持自定义插件开发）
import fastapi
import pydantic
import typing
import abc

class PluginBase(abc.ABC):
    def __init__(self, app: fastapi.FastAPI=None,config:pydantic.BaseSettings=None):
        if app is not None:
            self.init_app(app)
    
    @abc.abstractmethod
    def init_app(self, app: fastapi.FastAPI,config:pydantic.BaseSettings=None,*args, **kwargs)->None:
        raise NotImplementedError('需要实现初始化')
"""


class ApiExceptionHandler:
    """统一管理所有异常捕获"""

    def __init__(self, app=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if app is not None:
            self.init_app(app)

    def init_app(self, app: FastAPI):
        app.add_exception_handler(ValueError, handler=self.value_error_handler)
        app.add_exception_handler(AttributeError, handler=self.attribute_error_handler)
        app.add_exception_handler(
            BusinessError, handler=self.all_businewsserror_handler
        )
        app.add_exception_handler(
            RequestValidationError, handler=self.validation_exception_handler
        )
        app.add_exception_handler(
            StarletteHTTPException, handler=self.http_exception_handler
        )
        app.add_exception_handler(Exception, handler=self.all_exception_handler)

    async def validation_exception_handler(
        self, request: Request, exc: RequestValidationError
    ):
        """处理RequestValidationError"""
        logger.error(f"{request.url}")
        logger.error(f"{exc.errors()}")
        return ParameterException(
            http_status_code=400,
            api_code=400,
            message="参数校验错误",
            result={
                "detail": exc.errors(),
                "body": exc.body,
            },
        )

    async def all_businewsserror_handler(self, request: Request, exc: BusinessError):
        """处理BusinessError"""
        logger.error(f"{request.url}")
        logger.error(f"{exc.err_code}")
        logger.error(f"{exc.err_code_des}")
        return Businesserror(
            http_status_code=200, api_code=exc.err_code, message=exc.err_code_des
        )

    async def value_error_handler(self, request: Request, exc: ValueError):
        """处理ValueError"""
        error_trace = traceback.format_exc()
        logger.error(f"{request.url}")
        logger.error(f"{type(exc).__name__}")
        logger.error(f"{str(exc)}")
        return Fail(message=str(exc))

    async def attribute_error_handler(self, request: Request, exc: AttributeError):
        """处理AttributeError"""
        error_trace = traceback.format_exc()
        logger.error(f"{request.url}")
        logger.error(f"{type(exc).__name__}")
        logger.error(f"{str(exc)}")
        return Fail(message=f"属性错误: {str(exc)}")

    async def all_exception_handler(self, request: Request, exc: Exception):
        """对顶层所有的Exception进行处理"""
        error_trace = traceback.format_exc()
        logger.error(f"{request.url}")
        logger.error(f"{type(exc).__name__}")
        logger.error(f"{str(exc)}")
        return InternalServerErrorException()

    async def http_exception_handler(
        self, request: Request, exc: StarletteHTTPException
    ):
        """处理相关的HTTPException，根据不同状态码返回不同类型的响应报文"""
        logger.error(f"{request.url}")
        logger.error(f"{exc.status_code}")
        logger.error(f"{exc.detail}")
        if exc.status_code == 405:
            return MethodnotallowedException()
        elif exc.status_code == 404:
            return NotFoundException()
        elif exc.status_code == 429:
            return LimiterResException()
        elif exc.status_code == 500:
            return InternalServerErrorException()
        elif exc.status_code == 400:
            return BadrequestException(mes=exc.detail)
