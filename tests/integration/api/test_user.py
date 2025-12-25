import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.api.utils import assert_api_success, assert_api_failure
from tests.factories import UserFactory
from exts.exceptions.error_code import ErrorCode


@pytest.mark.asyncio
async def test_user_authentication_flow(client: AsyncClient, db_session: AsyncSession):
    """测试完整的用户认证流程：注册 -> 登录 -> 获取用户信息"""

    # 注册用户
    register_data = UserFactory.build_register_payload()
    response = await client.post("/api/register", json=register_data)
    user_data = assert_api_success(response)
    assert user_data["name"] == register_data["name"]
    user_id = user_data["id"]

    # 登录获取 token
    response = await client.post("/api/login", json=register_data)
    login_result = assert_api_success(response)
    assert "access_token" in login_result
    assert login_result["token_type"] == "bearer"
    access_token = login_result["access_token"]

    # 使用 token 获取用户信息
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/me", headers=headers)
    me_data = assert_api_success(response)
    assert me_data["id"] == user_id
    assert me_data["name"] == register_data["name"]


@pytest.mark.asyncio
async def test_get_user_info_without_token(client: AsyncClient):
    """测试未提供 token 时无法访问受保护接口"""
    response = await client.get("/api/me")
    assert_api_failure(response, expected_error=ErrorCode.UNAUTHORIZED)


@pytest.mark.asyncio
async def test_get_user_info_with_invalid_token(client: AsyncClient):
    """测试使用无效 token 时无法访问受保护接口"""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await client.get("/api/me", headers=headers)
    assert_api_failure(response, expected_error=ErrorCode.INVALID_TOKEN)
