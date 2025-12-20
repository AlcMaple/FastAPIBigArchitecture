import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import DesignUnitFactory
from tests.integration.api.utils import assert_api_success, assert_api_failure


@pytest.mark.asyncio
async def test_create_design_unit_success(client: AsyncClient):
    """
    测试场景：正常创建设计单位
    """
    payload = {
        "name": "广东建筑设计院",
        "tel": "13800138000",
        "email": "contact@gdarch.com",
        "address": "广州市天河区",
        "contact": "张工",
    }
    response = await client.post("/api/design_unit", json=payload)
    result = assert_api_success(response)
    assert result["name"] == payload["name"]
    assert result["email"] == payload["email"]
    assert result["id"] is not None
    assert result["created_at"] is not None


@pytest.mark.asyncio
async def test_create_design_unit_duplicate_name(
    client: AsyncClient, db_session: AsyncSession
):
    """
    测试场景：名称重复 (Error Code: 4041)
    """
    await DesignUnitFactory.create_async(session=db_session, name="广东建筑设计院")

    payload = {
        "name": "广东建筑设计院",  # 冲突点
        "tel": "13900000000",
    }

    response = await client.post("/api/design_unit", json=payload)
    assert_api_failure(
        response, expected_code=4041, match_msg="已存在", status_code=200
    )


@pytest.mark.parametrize(
    "field, bad_value, expected_msg",
    [
        # (字段名, 错误值, 期望包含的错误提示)
        ("email", "not-an-email", "邮箱格式"),  # 场景A: 邮箱格式
        ("tel", "123", "手机号格式"),  # 场景B: 手机号格式
    ],
)
@pytest.mark.asyncio
async def test_create_design_unit_validation_errors(
    client: AsyncClient, field, bad_value, expected_msg
):
    """
    测试场景：Pydantic 字段校验失败 (HTTP 422)
    """
    payload = {
        "name": "标准设计院",
        "tel": "13800138000",
        "email": "test@test.com",
    }
    payload[field] = bad_value
    response = await client.post("/api/design_unit", json=payload)
    assert_api_failure(response, status_code=422, match_msg=expected_msg)
