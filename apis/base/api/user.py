from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from exts.responses.api_response import Success
from exts.auth import get_current_user_id
from . import router_user
from ..schemas.user import UserRegisterRequest, UserLoginRequest
from ..services.user import UserService


@router_user.post("/register", summary="用户注册")
async def register(
    request: UserRegisterRequest,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    result = await UserService.register(db_session, request)
    return Success(result, message="注册成功")


@router_user.post("/login", summary="用户登录")
async def login(
    request: UserLoginRequest,
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    result = await UserService.login(db_session, request)
    return Success(result, message="登录成功")


@router_user.get("/me", summary="获取当前用户信息")
async def get_current_user(
    db_session: AsyncSession = Depends(depends_get_db_session),
    user_id: int = Depends(get_current_user_id),
):
    result = await UserService.get_current_user_info(db_session, user_id)
    return Success(result, message="获取用户信息成功")
