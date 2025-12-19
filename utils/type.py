"""
@File: type.py
@Description: 通用参数类型校验工具模块

基于 Pydantic V2，利用 Annotated 定义自带校验规则的类型。
在 Schema 中只需要声明类型，校验自动生效。

使用方式:
    from utils.type import NameStr, PhoneStr, ContactStr
    from pydantic import BaseModel, Field

    class DesignUnitCreateRequest(BaseModel):
        name: NameStr
        tel: Optional[PhoneStr] = None
        contact: Optional[ContactStr] = None
"""

from typing import Annotated, Optional
from pydantic import StringConstraints, BeforeValidator, Field
import re


# ============== 字符串长度校验类型 ==============

# 名称类型
NameStr = Annotated[
    str,
    StringConstraints(min_length=1, max_length=20, strip_whitespace=True),
    Field(description="名称"),
]

# 地址类型
AddressStr = Annotated[
    str,
    StringConstraints(min_length=1, max_length=200, strip_whitespace=True),
    Field(description="地址"),
]


# ============== 电话号码校验 ==============

# 中国大陆手机号
MOBILE_PHONE_PATTERN = r"^1[3-9]\d{9}$"

# 固定电话（区号-号码，支持带分机号）
# 格式：010-12345678、0571-87654321、010-12345678-1234
LANDLINE_PHONE_PATTERN = r"^0\d{2,3}-?\d{7,8}(-\d{1,6})?$"

# 通用电话（支持手机号、固话、400/800电话等）
GENERAL_PHONE_PATTERN = (
    r"^(1[3-9]\d{9}|0\d{2,3}-?\d{7,8}(-\d{1,6})?|400-?\d{7}|800-?\d{7})$"
)


def validate_phone(v: str) -> str:
    """
    验证电话号码格式

    支持格式：
    - 手机号：13812345678
    - 固话：010-12345678、0571-87654321
    - 带分机：010-12345678-1234
    - 400/800：400-1234567、800-1234567
    """
    v = v.strip()
    if not re.match(GENERAL_PHONE_PATTERN, v):
        raise ValueError("电话号码格式不正确，请输入有效的手机号或固定电话")
    return v


# 电话号码类型
PhoneStr = Annotated[
    str,
    BeforeValidator(validate_phone),
    Field(description="电话号码"),
]

# 手机号类型
MobilePhoneStr = Annotated[
    str,
    StringConstraints(pattern=MOBILE_PHONE_PATTERN, strip_whitespace=True),
    Field(description="手机号"),
]


# ============== 邮箱校验 ==============

# 邮箱
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def validate_email(v: str) -> str:
    """验证邮箱格式并转换为小写"""
    v = v.strip().lower()
    if not re.match(EMAIL_PATTERN, v):
        raise ValueError("邮箱格式不正确，请输入有效的邮箱地址")
    return v


# 邮箱类型
EmailStr = Annotated[
    str,
    BeforeValidator(validate_email),
    Field(description="邮箱地址"),
]
