import json
import time
import datetime
import decimal
import typing
from typing import Any, Dict, Optional, Union, List
from enum import Enum
from fastapi.responses import JSONResponse
from sqlalchemy.ext.declarative import DeclarativeMeta
from pydantic import BaseModel, Field


class CJsonEncoder(json.JSONEncoder):
    """
    自定义 JSONEncoder 类，用于序列化对象

    在使用 json.dumps() 进行数据结构转换时可以对传入的数据结构做不同的处理
    """

    def default(self, obj):
        if hasattr(obj, "keys") and hasattr(obj, "__getitem__"):
            return dict(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return str(obj, encoding="utf-8")
        elif isinstance(obj.__class__, DeclarativeMeta):
            # 如果是 models 类型，直接序列化 json 对象
            return self.default(
                {i.name: getattr(obj, i.name) for i in obj.__table__.columns}
            )
        elif isinstance(obj, dict):
            for k in obj:
                try:
                    if isinstance(
                        obj[k], (datetime.datetime, datetime.date, DeclarativeMeta)
                    ):
                        obj[k] = self.default(obj[k])
                    else:
                        obj[k] = obj[k]
                except TypeError:
                    obj[k] = None
            return obj
        return json.JSONEncoder.default(self, obj)


class ApiResponse(JSONResponse):
    """
    继承 JSONResponse 类，统一封装返回响应体内容
    """

    # 定义 HTTP 返回响应码，默认 200
    http_status_code = 200
    # 定义内部系统的错误内码，默认 0
    """
    - 200：当前请求处理正常
    - 1000～1999：当前用户提交参数校验异常
    - 2000～2999：登录用户信息异常或错误
    - 3000～3999：当前模块信息异常
    - 4000～4999：对接第三方接口异常
    - 5000～5999：当前系统内部异常
    """
    api_code = 0
    # 定义返回结果内容，默认为 None
    result: Optional[Dict[str, Any]] = None

    message = "成功"
    success = True
    timestamp = int(time.time() * 1000)

    def __init__(
        self,
        success=None,
        http_status_code=None,
        api_code=None,
        result=None,
        message=None,
        **options
    ):
        self.message = message or self.message
        self.success = success or self.success
        self.http_status_code = http_status_code or self.http_status_code
        self.api_code = api_code or self.api_code
        self.result = result or self.result

        # 返回内容体
        body = dict(
            message=self.message,
            success=self.success,
            timestamp=self.timestamp,
            result=self.result,
            code=self.api_code,
        )

        super(ApiResponse, self).__init__(
            status_code=self.http_status_code, content=body, **options
        )

    def render(self, content: typing.Any) -> bytes:
        """
        重写 render 方法，自动调用
        """
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CJsonEncoder,
        ).encode("utf-8")


class Success(ApiResponse):
    http_status_code = 200
    api_code = 200
    result = None
    message = "获取成功"
    success = True


class Fail(ApiResponse):
    http_status_code = 200
    api_code = 1000
    result = None
    message = "操作失败，参数异常"
    success = False


class InternalServerErrorException(ApiResponse):
    """内部服务器错误异常"""

    http_status_code = 500
    api_code = 5000
    result = None
    message = "内部服务器错误"
    success = False


class MethodnotallowedException(ApiResponse):
    """方法不被允许异常"""

    http_status_code = 405
    api_code = 4050
    result = None
    message = "请求方法不被允许"
    success = False


class NotFoundException(ApiResponse):
    """资源未找到异常"""

    http_status_code = 404
    api_code = 4040
    result = None
    message = "请求的资源未找到"
    success = False


class LimiterResException(ApiResponse):
    """请求频率限制异常"""

    http_status_code = 429
    api_code = 4290
    result = None
    message = "请求过于频繁，请稍后再试"
    success = False


class BadrequestException(ApiResponse):
    """错误请求异常"""

    http_status_code = 400
    api_code = 4000
    result = None
    message = "错误的请求"
    success = False

    def __init__(self, mes=None, **kwargs):
        if mes:
            kwargs["message"] = mes
        super().__init__(**kwargs)


class ParameterException(ApiResponse):
    """参数错误异常"""

    http_status_code = 400
    api_code = 1001
    result = None
    message = "参数错误"
    success = False


class Businesserror(ApiResponse):
    """业务逻辑错误异常"""

    http_status_code = 200
    api_code = 3000
    result = None
    message = "业务逻辑错误"
    success = False


class PermissionException(ApiResponse):
    """权限错误异常"""

    http_status_code = 403
    api_code = 2000
    result = None
    message = "权限不足"
    success = False


class AuthenticationException(ApiResponse):
    """认证错误异常"""

    http_status_code = 401
    api_code = 2001
    result = None
    message = "认证失败"
    success = False


class ValidationException(ApiResponse):
    """数据验证错误异常"""

    http_status_code = 422
    api_code = 1002
    result = None
    message = "数据验证失败"
    success = False


class DatabaseException(ApiResponse):
    """数据库操作异常"""

    http_status_code = 500
    api_code = 5001
    result = None
    message = "数据库操作异常"
    success = False


class ExternalServiceException(ApiResponse):
    """外部服务调用异常"""

    http_status_code = 502
    api_code = 4001
    result = None
    message = "外部服务调用失败"
    success = False
