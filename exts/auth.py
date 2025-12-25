"""
全局认证依赖项
"""

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.jwt import get_user_id_from_token
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode

security = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    从请求头中获取并验证 JWT token，返回当前用户ID

    Args:
        credentials: HTTP Bearer 认证凭据（由 FastAPI 自动从 Authorization header 解析）

    Returns:
        int: 当前用户ID

    Raises:
        ApiException: 当 token 无效或缺失时抛出异常
    """
    if not credentials:
        raise ApiException(ErrorCode.UNAUTHORIZED, "请先登录")

    token = credentials.credentials

    # 验证 token 并获取用户ID
    user_id = get_user_id_from_token(token)

    return user_id
