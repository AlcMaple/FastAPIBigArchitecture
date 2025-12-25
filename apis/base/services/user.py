from sqlalchemy.ext.asyncio import AsyncSession

from ..repository.user import UserRepository
from ..schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserLoginResponse,
    UserInfoResponse,
    UserBasicInfo,
)
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode
from utils.password import get_password_hash, verify_password
from utils.jwt import create_access_token


class UserService:
    @staticmethod
    async def register(
        db_session: AsyncSession, register_request: UserRegisterRequest
    ) -> UserInfoResponse:
        """用户注册"""
        # 检查用户名是否已存在
        if await UserRepository.check_user_exists(db_session, register_request.name):
            raise ApiException(ErrorCode.USER_ALREADY_EXISTS, "用户名已存在")

        # 创建用户
        user_data = register_request.model_dump(exclude={"password"})
        user_data["password_hash"] = get_password_hash(register_request.password)
        user_orm = await UserRepository.create_user(db_session, user_data)

        return UserInfoResponse.model_validate(user_orm)

    @staticmethod
    async def login(
        db_session: AsyncSession, login_request: UserLoginRequest
    ) -> UserLoginResponse:
        """用户登录"""
        # 根据用户名获取用户
        user_orm = await UserRepository.get_user_by_name(db_session, login_request.name)

        # 验证用户是否存在
        if not user_orm or not verify_password(
            login_request.password, user_orm.password_hash
        ):
            raise ApiException(ErrorCode.INVALID_CREDENTIALS, "用户名或密码错误")

        # 生成 JWT token
        access_token = create_access_token(data={"user_id": user_orm.id})

        user_basic = UserBasicInfo.model_validate(user_orm)
        return UserLoginResponse(
            access_token=access_token, token_type="bearer", **user_basic.model_dump()
        )

    @staticmethod
    async def get_current_user_info(
        db_session: AsyncSession, user_id: int
    ) -> UserInfoResponse:
        """获取当前用户信息"""
        user_orm = await UserRepository.get_user_by_id(db_session, user_id)

        if not user_orm:
            raise ApiException(ErrorCode.USER_NOT_FOUND, "用户不存在")

        return UserInfoResponse.model_validate(user_orm)
