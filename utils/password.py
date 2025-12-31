"""
密码工具函数
"""

from passlib.context import CryptContext
from starlette.concurrency import run_in_threadpool

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


async def get_password_hash(password: str) -> str:
    """
    对密码进行哈希加密（异步，CPU 密集型操作在线程池中执行）

    Args:
        password: 明文密码

    Returns:
        str: 哈希加密后的密码
    """
    return await run_in_threadpool(pwd_context.hash, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确（异步，CPU 密集型操作在线程池中执行）

    Args:
        plain_password: 明文密码
        hashed_password: 哈希加密后的密码

    Returns:
        bool: 密码是否匹配
    """
    return await run_in_threadpool(pwd_context.verify, plain_password, hashed_password)
