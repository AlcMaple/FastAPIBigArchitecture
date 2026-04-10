"""
全局认证依赖项
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.jwt import get_user_id_from_token

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
        HTTPException: 当 token 无效或缺失时
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="请先登录")

    token = credentials.credentials
    return get_user_id_from_token(token)
