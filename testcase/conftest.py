from typing import Generator, AsyncGenerator
import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import app
from db.database import depends_get_db_session
from db.models import *  # 确保所有模型都被导入，这样SQLModel.metadata才包含所有表


# 测试数据库配置 - 使用内存数据库或独立测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # 内存数据库，每次测试都重新创建


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于整个测试会话"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL, echo=False, pool_pre_ping=True  # 测试时不输出SQL
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # 清理：删除所有表
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """为每个测试提供独立的数据库会话"""
    TestSessionLocal = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestSessionLocal() as session:
        # 开始事务
        transaction = await session.begin()
        try:
            yield session
        finally:
            # 回滚事务，确保测试间数据隔离
            await transaction.rollback()
            await session.close()


@pytest.fixture
async def override_get_db(db_session: AsyncSession):
    """覆盖数据库依赖"""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[depends_get_db_session] = _override_get_db
    yield
    # 清理覆盖
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """同步测试客户端 - 用于向后兼容"""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def async_client(override_get_db):
    """异步测试客户端 - 推荐使用"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient) -> AsyncClient:
    """已认证的异步客户端（如果需要认证的话）"""
    # 这里可以添加认证逻辑，比如登录获取token
    # response = await async_client.post("/auth/login", json={"username": "test", "password": "test"})
    # token = response.json()["access_token"]
    # async_client.headers.update({"Authorization": f"Bearer {token}"})

    return async_client


# 配置 pytest-asyncio
pytest_plugins = ("pytest_asyncio",)
