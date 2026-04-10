"""
用户接口黑盒集成测试

运行方式:
    pytest tests/test_user.py -v
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app import app

BASE_URL = "http://test"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as c:
        yield c


async def test_register_success(client: AsyncClient):
    """正常注册用户"""
    payload = {"name": "testuser1", "password": "Test123456"}
    resp = await client.post("/api/register", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == payload["name"]
    assert "id" in body["data"]


async def test_register_duplicate(client: AsyncClient):
    """重复注册应返回 409"""
    payload = {"name": "dupuser1", "password": "Test123456"}
    await client.post("/api/register", json=payload)
    resp = await client.post("/api/register", json=payload)
    assert resp.status_code == 409
    assert resp.json()["success"] is False


async def test_login_success(client: AsyncClient):
    """正常登录，返回 access_token"""
    payload = {"name": "loginuser1", "password": "Test123456"}
    await client.post("/api/register", json=payload)

    resp = await client.post("/api/login", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    """密码错误应返回 401"""
    payload = {"name": "wrongpwduser", "password": "Test123456"}
    await client.post("/api/register", json=payload)

    resp = await client.post("/api/login", json={"name": "wrongpwduser", "password": "Wrong123"})
    assert resp.status_code == 401
    assert resp.json()["success"] is False


async def test_get_me_success(client: AsyncClient):
    """使用有效 token 获取用户信息"""
    payload = {"name": "meuser1", "password": "Test123456"}
    await client.post("/api/register", json=payload)
    login_resp = await client.post("/api/login", json=payload)
    token = login_resp.json()["data"]["access_token"]

    resp = await client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["name"] == payload["name"]


async def test_get_me_without_token(client: AsyncClient):
    """未提供 token 应返回 401"""
    resp = await client.get("/api/me")
    assert resp.status_code == 401
    assert resp.json()["success"] is False


async def test_get_me_invalid_token(client: AsyncClient):
    """无效 token 应返回 401"""
    resp = await client.get("/api/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
    assert resp.json()["success"] is False


async def test_register_validation_error(client: AsyncClient):
    """用户名格式不合法应返回 400"""
    payload = {"name": "a", "password": "Test123456"}  # 用户名太短
    resp = await client.post("/api/register", json=payload)
    assert resp.status_code == 400
    assert resp.json()["success"] is False
