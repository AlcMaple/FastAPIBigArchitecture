from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import re


class UserRegisterRequest(BaseModel):
    """用户注册请求"""

    name: str = Field(..., min_length=3, max_length=10, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证用户名格式"""
        if not re.match(r"^[a-zA-Z0-9_\u4e00-\u9fa5]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线和中文")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]+$", v):
            raise ValueError("密码必须包含字母和数字")
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""

    name: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserBasicInfo(BaseModel):
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")

    model_config = ConfigDict(from_attributes=True)


class UserLoginResponse(UserBasicInfo):
    """用户登录响应"""

    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class UserInfoResponse(UserBasicInfo):
    """用户信息响应"""

    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
