"""
集成测试配置
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app import app
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from tests.factories import UserFactory
from config.settings import settings


# 测试数据库 URL (使用内存 SQLite)
TEST_DB_URL = settings.test_database_url


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    数据库会话 fixture
    """
    # 创建测试数据库引擎
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,  # 禁用 SQL 查询日志
        connect_args={"check_same_thread": False},
    )

    # 防止 commit 后属性过期导致无法读取
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    # 建表
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # 提供 Session 测试用例
    async with async_session() as session:
        yield session

    # 删表
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    # 关闭引擎
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    HTTP 测试客户端 fixture
    """

    # 覆盖依赖
    def override_get_db():
        return db_session

    def override_get_db_with_transaction():
        return db_session

    app.dependency_overrides[depends_get_db_session] = override_get_db
    app.dependency_overrides[depends_get_db_session_with_transaction] = (
        override_get_db_with_transaction
    )

    # 创建异步 HTTP 客户端
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # 测试结束后清理依赖覆盖
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def clean_db(db_session):
    """
    清空数据库 fixture
    """
    # 清空所有表的数据 (保留表结构)
    async with db_session.begin():
        for table in reversed(SQLModel.metadata.sorted_tables):
            await db_session.execute(table.delete())
    yield
