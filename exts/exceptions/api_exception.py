"""
统一的 API 异常类
"""

from typing import Any, Dict, Optional
from .error_code import ErrorCode


class ApiException(Exception):
    """
    统一的 API 异常类
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        data: Optional[Any] = None,
        **kwargs,
    ):
        """
        初始化异常
        """
        self.error_code = error_code
        self.message = message or error_code.message
        self.data = data
        self.http_status = error_code.http_status
        self.kwargs = kwargs

        super().__init__(self.message)

    @property
    def code(self) -> int:
        """获取错误码"""
        return self.error_code.code

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.data is not None:
            result["data"] = self.data
        return result

    def __str__(self):
        return f"ApiException({self.error_code.name}, code={self.code}, message='{self.message}')"

    def __repr__(self):
        return self.__str__()
