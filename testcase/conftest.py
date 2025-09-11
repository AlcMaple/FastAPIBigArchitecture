import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging
import os
import asyncio

# 确保运行到项目根目录
sys.path.append(str(Path(__file__).parent.parent))

# 日志配置
from loguru import logger

os.environ["TESTING"] = "true"
logging.disable(logging.CRITICAL)
logger.remove()
logger.add(lambda _: None)

from app import app
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from config.settings import settings
from utils.create_test_tables import create_tables_sync
from utils.drop_test_tables import drop_tables_sync


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_test_tables():
    """自动创建和删除测试数据库表"""

    # 前置：创建测试数据库表
    if not create_tables_sync():
        raise Exception("Failed to create test tables")

    yield  # 测试运行期间

    # 后置：删除测试数据库表
    drop_tables_sync()


# 测试引擎
test_engine = create_async_engine(
    settings.test_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=1,
    max_overflow=0,
)

test_session_factory = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture
async def test_db_session():
    """测试数据库会话"""
    async with test_session_factory() as session:
        yield session


@pytest.fixture(scope="function")
def client():
    """创建测试客户端，覆盖数据库依赖"""

    async def override_get_db_session():
        """覆盖数据库会话依赖（查询）"""
        async with test_session_factory() as session:
            yield session

    async def override_get_db_session_with_transaction():
        """覆盖带事务管理的数据库会话依赖（增删改）"""
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # 依赖覆盖
    app.dependency_overrides[depends_get_db_session] = override_get_db_session
    app.dependency_overrides[depends_get_db_session_with_transaction] = (
        override_get_db_session_with_transaction
    )

    try:
        with TestClient(app) as c:
            yield c
    finally:
        # 清理依赖覆盖
        app.dependency_overrides.clear()
