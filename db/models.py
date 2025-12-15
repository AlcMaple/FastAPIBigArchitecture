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
    name: str = Field(max_length=10, description="用户名")
    password: str = Field(description="密码")
    password_hash: str = Field(description="密码哈希")
