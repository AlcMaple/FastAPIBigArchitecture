import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import sys
from pathlib import Path
import logging
import os

# 确保运行到项目根目录
sys.path.append(str(Path(__file__).parent.parent))

# 日志配置
from loguru import logger

os.environ["TESTING"] = "true"
logging.disable(logging.CRITICAL)
logger.remove()
logger.add(lambda _: None)

from app import app
from db.database import depends_get_db_session
from config.settings import settings


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        settings.test_database_url, echo=settings.database_echo
    )
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine):
    AsyncTestSession = sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with AsyncTestSession() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[depends_get_db_session] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
