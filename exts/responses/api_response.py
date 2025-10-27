"""
统一的 API 响应类
"""

import json
import time
import datetime
import decimal
from typing import Any, Optional
from fastapi.responses import JSONResponse
from sqlalchemy.ext.declarative import DeclarativeMeta


class CustomJSONEncoder(json.JSONEncoder):
    """自定义 JSON 编码器"""

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
            # SQLAlchemy models
            return {i.name: getattr(obj, i.name) for i in obj.__table__.columns}
        elif isinstance(obj, dict):
            for k in obj:
                try:
                    if isinstance(
                        obj[k], (datetime.datetime, datetime.date, DeclarativeMeta)
                    ):
                        obj[k] = self.default(obj[k])
                except TypeError:
                    obj[k] = None
            return obj
        return json.JSONEncoder.default(self, obj)


class ApiResponse(JSONResponse):
    """
    统一的 API 响应基类

    响应格式:
    {
        "success": true/false,
        "code": 200,
        "message": "操作成功",
        "data": {...},
        "timestamp": 1678886400000
    }
    """

    def __init__(
        self,
        success: bool = True,
        code: int = 200,
        message: str = "操作成功",
        data: Any = None,
        http_status: int = 200,
        **kwargs,
    ):
        """
        初始化响应

        Args:
            success: 业务是否成功
            code: API 业务码
            message: 提示消息
            data: 业务数据
            http_status: HTTP 状态码
        """
        body = {
            "success": success,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }

        super().__init__(status_code=http_status, content=body, **kwargs)

    def render(self, content: Any) -> bytes:
        """重写 render 方法，使用自定义 JSON 编码器"""
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJSONEncoder,
        ).encode("utf-8")


class Success(ApiResponse):
    """
    成功响应

    使用方式:
        # 基本用法
        return Success()

        # 携带数据
        return Success(data={"user_id": 123})

        # 自定义消息
        return Success(data=doctor_info, message="医生信息获取成功")
    """

    def __init__(
        self,
        data: Any = None,
        message: str = "操作成功",
        **kwargs,
    ):
        super().__init__(
            success=True,
            code=200,
            message=message,
            data=data,
            http_status=200,
            **kwargs,
        )


class Error(ApiResponse):
    """
    错误响应
    """

    def __init__(
        self,
        code: int,
        message: str,
        data: Any = None,
        http_status: int = 200,
        **kwargs,
    ):
        super().__init__(
            success=False,
            code=code,
            message=message,
            data=data,
            http_status=http_status,
            **kwargs,
        )
