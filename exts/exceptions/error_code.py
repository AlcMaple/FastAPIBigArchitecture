"""
错误码枚举
"""

from enum import Enum


class ErrorCode(Enum):
    """
    错误码枚举

    格式: 错误名称 = (错误码, "默认错误消息")

    错误码分类规则:
    - 200: 成功
    - 1000-1999: 参数校验错误
    - 2000-2999: 认证和权限错误
    - 3000-3999: 业务逻辑错误
    - 4000-4999: 资源和外部服务错误
    - 5000-5999: 系统内部错误
    """

    # ==================== 成功 (200) ====================
    SUCCESS = (200, "操作成功")

    # ==================== 参数错误 (1000-1999) ====================
    PARAMETER_ERROR = (1001, "参数错误")
    MISSING_PARAMETER = (1002, "缺少必填参数")
    INVALID_PARAMETER_FORMAT = (1003, "参数格式错误")
    PARAMETER_OUT_OF_RANGE = (1004, "参数值超出允许范围")
    VALIDATION_ERROR = (1010, "数据验证失败")

    # ==================== 认证错误 (2000-2099) ====================
    UNAUTHORIZED = (2001, "未登录或登录已过期")
    INVALID_TOKEN = (2002, "无效的认证令牌")
    TOKEN_EXPIRED = (2003, "认证令牌已过期")
    INVALID_CREDENTIALS = (2004, "用户名或密码错误")

    # ==================== 权限错误 (2100-2199) ====================
    FORBIDDEN = (2100, "权限不足")
    ACCESS_DENIED = (2101, "访问被拒绝")
    ROLE_PERMISSION_DENIED = (2102, "角色权限不足")

    # ==================== 资源错误 (4000-4099) ====================
    NOT_FOUND = (4040, "请求的资源不存在")
    RESOURCE_ALREADY_EXISTS = (4041, "资源已存在")
    RESOURCE_CONFLICT = (4042, "资源冲突")

    # ==================== 外部服务错误 (4100-4199) ====================
    EXTERNAL_SERVICE_ERROR = (4100, "外部服务调用失败")
    SMS_SERVICE_ERROR = (4101, "短信服务异常")
    PAYMENT_SERVICE_ERROR = (4102, "支付服务异常")
    EMAIL_SERVICE_ERROR = (4103, "邮件服务异常")

    # ==================== 请求错误 (4200-4299) ====================
    BAD_REQUEST = (4200, "错误的请求")
    METHOD_NOT_ALLOWED = (4201, "请求方法不被允许")
    RATE_LIMIT_EXCEEDED = (4290, "请求过于频繁，请稍后再试")

    # ==================== 业务逻辑错误 (3000-3999) ====================
    BUSINESS_ERROR = (3000, "业务处理失败")

    # 用户相关 (3100-3199)
    USER_NOT_FOUND = (3101, "用户不存在")
    USER_ALREADY_EXISTS = (3102, "用户已存在")
    USER_DISABLED = (3103, "用户已被禁用")
    USER_REGISTRATION_FAILED = (3104, "用户注册失败")

    # ==================== 数据库错误 (5000-5099) ====================
    DATABASE_ERROR = (5001, "数据库操作异常")
    DATABASE_CONNECTION_ERROR = (5002, "数据库连接失败")
    DUPLICATE_KEY_ERROR = (5003, "数据重复，违反唯一性约束")
    FOREIGN_KEY_ERROR = (5004, "外键约束错误")

    # ==================== 系统错误 (5100-5999) ====================
    INTERNAL_SERVER_ERROR = (5100, "系统内部错误")
    SERVICE_UNAVAILABLE = (5101, "服务暂时不可用")
    CONFIGURATION_ERROR = (5102, "系统配置错误")

    @property
    def code(self) -> int:
        """获取错误码"""
        return self.value[0]

    @property
    def message(self) -> str:
        """获取默认错误消息"""
        return self.value[1]

    def __str__(self):
        return f"{self.name}({self.code}): {self.message}"
