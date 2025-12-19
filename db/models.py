from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


# ====================================================
# 简单路由数据模型
# ====================================================
class User(BaseModel, table=True):
    """用户表"""

    __tablename__ = "user"

    name: str = Field(max_length=10, description="用户名")
    password: str = Field(description="密码")
    password_hash: str = Field(description="密码哈希")


class DesignUnit(BaseModel, table=True):
    """设计单位表"""

    __tablename__ = "design_unit"

    name: str = Field(..., description="设计单位名称")
    tel: Optional[str] = Field(default=None, description="联系电话")
    email: Optional[str] = Field(default=None, description="邮箱")
    address: Optional[str] = Field(default=None, description="地址")
    contact: Optional[str] = Field(default=None, description="联系人")
