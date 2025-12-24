"""
错误码枚举
"""

from enum import Enum
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)


class ErrorCode(Enum):
    """
    错误码枚举

    格式: 错误名称 = (错误码, "默认错误消息", HTTP状态码)

    错误码分类规则:
    - 200: 成功
    - 1000-1999: 参数校验错误
    - 2000-2999: 认证和权限错误
    - 3000-3999: 业务逻辑错误
    - 4000-4999: 资源和外部服务错误
    - 5000-5999: 系统内部错误
    """

    # ==================== 成功 (200) ====================
    SUCCESS = (200, "操作成功", HTTP_200_OK)

    # ==================== 参数错误 (1000-1999) ====================
    PARAMETER_ERROR = (1001, "参数错误", HTTP_400_BAD_REQUEST)
    MISSING_PARAMETER = (1002, "缺少必填参数", HTTP_400_BAD_REQUEST)
    INVALID_PARAMETER_FORMAT = (1003, "参数格式错误", HTTP_400_BAD_REQUEST)
    PARAMETER_OUT_OF_RANGE = (1004, "参数值超出允许范围", HTTP_400_BAD_REQUEST)
    VALIDATION_ERROR = (1010, "数据验证失败", HTTP_422_UNPROCESSABLE_CONTENT)

    # ==================== 认证错误 (2000-2099) ====================
    UNAUTHORIZED = (2001, "未登录或登录已过期", HTTP_401_UNAUTHORIZED)
    INVALID_TOKEN = (2002, "无效的认证令牌", HTTP_401_UNAUTHORIZED)
    TOKEN_EXPIRED = (2003, "认证令牌已过期", HTTP_401_UNAUTHORIZED)
    INVALID_CREDENTIALS = (2004, "用户名或密码错误", HTTP_401_UNAUTHORIZED)

    # ==================== 权限错误 (2100-2199) ====================
    FORBIDDEN = (2100, "权限不足", HTTP_403_FORBIDDEN)
    ACCESS_DENIED = (2101, "访问被拒绝", HTTP_403_FORBIDDEN)
    ROLE_PERMISSION_DENIED = (2102, "角色权限不足", HTTP_403_FORBIDDEN)

    # ==================== 业务逻辑错误 (3000-3999) ====================
    BUSINESS_ERROR = (3000, "业务处理失败", HTTP_400_BAD_REQUEST)

    # 用户相关 (3100-3199)
    USER_NOT_FOUND = (3101, "用户不存在", HTTP_404_NOT_FOUND)
    USER_ALREADY_EXISTS = (3102, "用户已存在", HTTP_409_CONFLICT)
    USER_DISABLED = (3103, "用户已被禁用", HTTP_403_FORBIDDEN)
    USER_REGISTRATION_FAILED = (3104, "用户注册失败", HTTP_400_BAD_REQUEST)

    # ==================== 资源错误 (4000-4099) ====================
    NOT_FOUND = (4040, "请求的资源不存在", HTTP_404_NOT_FOUND)
    RESOURCE_ALREADY_EXISTS = (4041, "资源已存在", HTTP_409_CONFLICT)
    RESOURCE_CONFLICT = (4042, "资源冲突", HTTP_409_CONFLICT)

    # ==================== 外部服务错误 (4100-4199) ====================
    EXTERNAL_SERVICE_ERROR = (4100, "外部服务调用失败", HTTP_503_SERVICE_UNAVAILABLE)
    SMS_SERVICE_ERROR = (4101, "短信服务异常", HTTP_503_SERVICE_UNAVAILABLE)
    PAYMENT_SERVICE_ERROR = (4102, "支付服务异常", HTTP_503_SERVICE_UNAVAILABLE)
    EMAIL_SERVICE_ERROR = (4103, "邮件服务异常", HTTP_503_SERVICE_UNAVAILABLE)

    # ==================== 请求错误 (4200-4299) ====================
    BAD_REQUEST = (4200, "错误的请求", HTTP_400_BAD_REQUEST)
    METHOD_NOT_ALLOWED = (4201, "请求方法不被允许", HTTP_405_METHOD_NOT_ALLOWED)
    RATE_LIMIT_EXCEEDED = (4290, "请求过于频繁，请稍后再试", HTTP_429_TOO_MANY_REQUESTS)

    # ==================== 数据库错误 (5000-5099) ====================
    DATABASE_ERROR = (5001, "数据库操作异常", HTTP_500_INTERNAL_SERVER_ERROR)
    DATABASE_CONNECTION_ERROR = (5002, "数据库连接失败", HTTP_500_INTERNAL_SERVER_ERROR)
    DUPLICATE_KEY_ERROR = (5003, "数据重复，违反唯一性约束", HTTP_409_CONFLICT)
    FOREIGN_KEY_ERROR = (5004, "外键约束错误", HTTP_400_BAD_REQUEST)

    # ==================== 系统错误 (5100-5999) ====================
    INTERNAL_SERVER_ERROR = (
        5100,
        "系统内部错误，请联系管理员",
        HTTP_500_INTERNAL_SERVER_ERROR,
    )
    SERVICE_UNAVAILABLE = (5101, "服务暂时不可用", HTTP_503_SERVICE_UNAVAILABLE)
    CONFIGURATION_ERROR = (5102, "系统配置错误", HTTP_500_INTERNAL_SERVER_ERROR)

    @property
    def code(self) -> int:
        """获取错误码"""
        return self.value[0]

    @property
    def message(self) -> str:
        """获取默认错误消息"""
        return self.value[1]

    @property
    def http_status(self) -> int:
        """获取HTTP状态码"""
        return self.value[2]

    def __str__(self):
        return f"[{self.http_status}] {self.name}({self.code}): {self.message}"
