"""
@File: type.py
@Description: 通用参数类型校验工具模块
"""

from typing import Annotated
from pydantic import BeforeValidator, Field
import re


# ============== 通用辅助函数 ==============


def validate_str_length(v: str, name: str, max_len: int, min_len: int = 1) -> str:
    """
    通用字符串长度校验
    :param v: 输入值
    :param name: 字段名称（用于报错提示）
    :param max_len: 最大长度
    :param min_len: 最小长度
    """
    if v is None:
        raise ValueError(f"{name}不能为空")

    v = str(v).strip()

    if len(v) < min_len:
        raise ValueError(f"{name}长度不能少于{min_len}个字符")

    if len(v) > max_len:
        raise ValueError(f"{name}长度不能超过{max_len}个字符")

    return v


# ============== 字符串长度校验类型 ==============


def validate_name(v: str) -> str:
    return validate_str_length(v, "名称", max_len=20)


def validate_address(v: str) -> str:
    return validate_str_length(v, "地址", max_len=200)


# 名称类型
NameStr = Annotated[
    str,
    BeforeValidator(validate_name),
    Field(description="名称", examples=["广东建筑设计院"]),
]

# 地址类型
AddressStr = Annotated[
    str,
    BeforeValidator(validate_address),
    Field(description="地址", examples=["广州市天河区科韵路88号"]),
]


# ============== 电话号码校验 ==============

# 正则表达式常量
MOBILE_PHONE_PATTERN = r"^1[3-9]\d{9}$"
LANDLINE_PHONE_PATTERN = r"^0\d{2,3}-?\d{7,8}(-\d{1,6})?$"
GENERAL_PHONE_PATTERN = (
    r"^(1[3-9]\d{9}|0\d{2,3}-?\d{7,8}(-\d{1,6})?|400-?\d{7}|800-?\d{7})$"
)


def validate_mobile(v: str) -> str:
    """验证纯手机号"""
    v = str(v).strip()
    if not v:
        raise ValueError("手机号不能为空")

    if not re.match(MOBILE_PHONE_PATTERN, v):
        raise ValueError("手机号格式不正确，请输入有效的11位中国大陆手机号码")
    return v


def validate_general_phone(v: str) -> str:
    """验证通用电话（手机/座机/400）"""
    v = str(v).strip()
    if not v:
        raise ValueError("电话号码不能为空")

    if not re.match(GENERAL_PHONE_PATTERN, v):
        raise ValueError("电话号码格式不正确，支持手机号、座机(带区号)或400热线")
    return v


# 手机号类型
MobilePhoneStr = Annotated[
    str,
    BeforeValidator(validate_mobile),
    Field(description="手机号", pattern=MOBILE_PHONE_PATTERN, examples=["13800138000"]),
]

# 通用电话类型
PhoneStr = Annotated[
    str,
    BeforeValidator(validate_general_phone),
    Field(description="电话号码", examples=["020-88888888", "13800138000"]),
]


# ============== 邮箱校验 ==============

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def validate_email(v: str) -> str:
    """验证邮箱格式并转换为小写"""
    v = str(v).strip().lower()
    if not v:
        raise ValueError("邮箱地址不能为空")

    if not re.match(EMAIL_PATTERN, v):
        raise ValueError("邮箱格式不正确，请输入有效的邮箱地址(如: example@domain.com)")
    return v


# 邮箱类型
EmailStr = Annotated[
    str,
    BeforeValidator(validate_email),
    Field(description="邮箱地址", examples=["contact@example.com"]),
]
