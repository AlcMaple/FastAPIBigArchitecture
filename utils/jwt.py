"""
JWT Token 工具函数
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt

from config.settings import settings
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT access token
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    # 设置过期时间
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    # 添加过期时间和签发时间到 payload
    to_encode.update({"exp": expire, "iat": now})

    # 生成 token
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    验证并解析 JWT token

    Args:
        token: JWT token 字符串

    Returns:
        Dict[str, Any]: 解码后的 payload 数据

    Raises:
        ApiException: 当 token 无效或过期时抛出异常
    """
    try:
        # 验证并解码 token
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token 过期
        raise ApiException(ErrorCode.TOKEN_EXPIRED, "认证令牌已过期")
    except jwt.InvalidTokenError:
        # Token 无效
        raise ApiException(ErrorCode.INVALID_TOKEN, "无效的认证令牌")


def get_user_id_from_token(token: str) -> int:
    payload = verify_token(token)

    user_id = payload.get("user_id")
    if user_id is None:
        raise ApiException(ErrorCode.INVALID_TOKEN, "Token 中缺少用户ID")

    return int(user_id)
