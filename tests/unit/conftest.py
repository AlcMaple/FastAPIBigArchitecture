"""
单元测试配置 - 提供常用的 Mock 对象，隔离外部依赖
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_db_session():
    """
    【Mock】数据库会话
    """
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_redis():
    """
    【Mock】Redis
    """
    m = AsyncMock()
    # 模拟 get 方法默认返回 None
    m.get.return_value = None
    # 模拟 set 方法成功
    m.set.return_value = True
    # 模拟 delete 方法成功
    m.delete.return_value = 1
    # 模拟 exists 方法
    m.exists.return_value = False
    return m


@pytest.fixture
def mock_email_sender():
    """
    【Mock】邮件发送服务
    """
    m = AsyncMock()
    m.send_email.return_value = {"status": "sent", "message_id": "test_123"}
    return m


@pytest.fixture
def mock_sms_sender():
    """
    【Mock】短信发送服务
    """
    m = AsyncMock()
    m.send_sms.return_value = {"success": True, "code": "123456"}
    return m


@pytest.fixture
def mock_file_storage():
    """
    【Mock】文件存储服务
    """
    m = AsyncMock()
    m.upload.return_value = "/uploads/test_file.jpg"
    m.download.return_value = b"fake file content"
    m.delete.return_value = True
    return m


@pytest.fixture
def mock_current_user():
    """
    【Mock】当前登录用户
    """
    user = MagicMock()
    user.id = 1
    user.name = "unit_test_user"
    user.is_active = True
    return user


@pytest.fixture
def mock_http_client():
    """
    【Mock】HTTP 客户端
    """
    m = AsyncMock()
    m.get.return_value = MagicMock(
        status_code=200, json=lambda: {"status": "ok", "data": {}}
    )
    m.post.return_value = MagicMock(
        status_code=200, json=lambda: {"status": "ok", "id": 123}
    )
    return m
