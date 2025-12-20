import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
import logging
import os
import subprocess

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
from tests.manager import manager


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_test_tables():
    """自动创建和删除测试数据库表"""

    # 前置：创建测试数据库表
    if not create_tables_sync():
        raise Exception(f"Failed to create {settings.test_db_type} test tables")

    # 导入基础数据
    print("开始导入测试基础数据...")
    project_root = Path(__file__).parent.parent

    for script_path in settings.test_data_import_scripts:
        script_name = Path(script_path).stem
        print(f"执行: {script_path}")

        result = subprocess.run(
            [sys.executable, script_path],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"  {script_name} 执行失败: {result.stderr}")
        else:
            print(f"  {script_name} 执行成功")

    yield  # 测试运行期间

    # 后置：删除测试数据库表
    if settings.test_db_type == "mysql":
        drop_tables_sync()


# 获取测试数据库管理器的引擎和会话
def get_test_engine_and_session():
    """获取测试数据库引擎和会话"""
    engine = manager.get_engine()
    session = manager.get_session()
    return engine, session


test_engine, test_session = get_test_engine_and_session()


@pytest.fixture
async def test_db_session():
    """测试数据库会话"""
    async with test_session() as session:
        yield session


@pytest.fixture(scope="function")
def client():
    """创建测试客户端，覆盖数据库依赖"""

    async def override_get_db_session():
        """覆盖数据库会话依赖（查询）"""
        async with test_session() as session:
            yield session

    async def override_get_db_session_with_transaction():
        """覆盖带事务管理的数据库会话依赖（增删改）"""
        async with test_session() as session:
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
