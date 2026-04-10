from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import re

from exts.route import JsonRoute
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from db.models import User
from utils.password import get_password_hash, verify_password
from utils.jwt import create_access_token, get_user_id_from_token

# ======================== Schemas ========================

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    name: str = Field(..., min_length=3, max_length=10, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]+$", v):
            raise ValueError("密码必须包含字母和数字")
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    name: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserLoginResponse(BaseModel):
    """用户登录响应"""
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")

    model_config = ConfigDict(from_attributes=True)


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ======================== Router ========================

router = APIRouter(prefix="/api", tags=["用户"], route_class=JsonRoute)

_security = HTTPBearer(auto_error=False)


def _get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> int:
    """从 Bearer Token 中解析当前用户ID"""
    if not credentials:
        raise HTTPException(status_code=401, detail="请先登录")
    return get_user_id_from_token(credentials.credentials)


@router.post("/register", summary="用户注册")
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    result = await db.execute(select(User).where(User.name == payload.name))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail="用户名已存在")

    password_hash = await get_password_hash(payload.password)
    user = User(name=payload.name, password_hash=password_hash)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return UserInfoResponse.model_validate(user)


@router.post("/login", summary="用户登录")
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(depends_get_db_session),
):
    result = await db.execute(select(User).where(User.name == payload.name))
    user = result.scalars().first()

    if not user or not await verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_access_token(data={"user_id": user.id})
    return UserLoginResponse(
        id=user.id,
        name=user.name,
        access_token=access_token,
        token_type="bearer",
    )


@router.get("/me", summary="获取当前用户信息")
async def get_current_user(
    db: AsyncSession = Depends(depends_get_db_session),
    user_id: int = Depends(_get_current_user_id),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserInfoResponse.model_validate(user)
