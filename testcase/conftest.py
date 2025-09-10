import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import logging
import os
import tempfile
import shutil

# 确保运行到项目根目录
sys.path.append(str(Path(__file__).parent.parent))

# 日志配置
from loguru import logger

os.environ["TESTING"] = "true"
logging.disable(logging.CRITICAL)
logger.remove()
logger.add(lambda _: None)

from app import app
from db.database import JsonDatabase, json_db
from config.settings import settings


@pytest.fixture(scope="session")
def test_data_dir():
    """创建测试用的临时数据目录"""
    temp_dir = tempfile.mkdtemp(prefix="test_data_")
    yield temp_dir
    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_json_db(test_data_dir):
    """创建测试用的JSON数据库实例"""
    # 使用临时目录
    original_data_dir = settings.data_dir
    settings.data_dir = test_data_dir

    # 创建测试用的JSON数据库实例
    test_db = JsonDatabase()

    yield test_db

    # 恢复原始设置
    settings.data_dir = original_data_dir


@pytest.fixture
def client(test_json_db):
    """创建测试客户端"""
    # 重写全局JSON数据库实例
    original_json_db = json_db
    import db.database

    db.database.json_db = test_json_db

    with TestClient(app) as c:
        yield c

    # 恢复原始实例
    db.database.json_db = original_json_db
