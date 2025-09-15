from sqlmodel import create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from config.settings import settings


# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_timeout=settings.pool_timeout,
    pool_recycle=settings.pool_recycle,
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


'''
函数正常结束 → 自动commit()
抛出异常 → 自动rollback()
'''
@asynccontextmanager
async def get_async_session_with_transaction() -> AsyncGenerator[AsyncSession, None]:
    """获取自动事务管理的异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 自动提交事务
            await session.commit()
        except Exception:
            # 自动回滚
            await session.rollback()
            raise
        finally:
            await session.close()


# 依赖注入函数
async def depends_get_db_session():
    """数据库会话依赖注入"""
    async with get_async_session() as session:
        yield session


async def depends_get_db_session_with_transaction():
    """数据库会话依赖注入（带自动事务管理）"""
    async with get_async_session_with_transaction() as session:
        yield session
