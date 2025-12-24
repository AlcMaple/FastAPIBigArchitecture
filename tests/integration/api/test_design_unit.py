import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from datetime import datetime

from tests.factories import DesignUnitFactory
from tests.integration.api.utils import assert_api_success, assert_api_failure
from exts.exceptions.error_code import ErrorCode


@pytest.mark.asyncio
async def test_create_design_unit_success(client: AsyncClient):
    """
    测试场景：正常创建设计单位
    """
    payload = DesignUnitFactory.build_payload()
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
    conflict_name = "恒大地产设计院"
    await DesignUnitFactory.create_async(session=db_session, name=conflict_name)
    payload = DesignUnitFactory.build_payload(name=conflict_name)
    response = await client.post("/api/design_unit", json=payload)
    assert_api_failure(
        response, expected_error=ErrorCode.RESOURCE_ALREADY_EXISTS, match_msg="已存在"
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
    测试场景：Pydantic 字段校验失败 (HTTP 400)
    """
    payload = DesignUnitFactory.build_payload()
    payload[field] = bad_value
    response = await client.post("/api/design_unit", json=payload)
    assert_api_failure(
        response, expected_error=ErrorCode.PARAMETER_ERROR, match_msg=expected_msg
    )


@pytest.mark.asyncio
async def test_update_design_unit_updates_timestamp(
    client: AsyncClient, db_session: AsyncSession
):
    """
    测试场景：更新设计单位后，updated_at 时间戳发生变化
    """
    # 创建设计单位
    unit = await DesignUnitFactory.create_async(session=db_session, name="原始设计院")
    original_updated_at = unit.updated_at

    # 等待至少 1 秒确保时间戳变化
    await asyncio.sleep(1.1)

    # 更新设计单位
    update_payload = DesignUnitFactory.build_payload(
        name="更新后的设计院", contact="新联系人"
    )
    response = await client.put(f"/api/design_unit/{unit.id}", json=update_payload)
    result = assert_api_success(response)

    # 验证更新时间已变化
    updated_at_str = result["updated_at"]
    new_updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
    assert (
        new_updated_at > original_updated_at
    ), f"更新后的 updated_at ({new_updated_at}) 应该大于原始值 ({original_updated_at})"

    # 验证其他字段
    assert result["name"] == "更新后的设计院"
    assert result["contact"] == "新联系人"


@pytest.mark.asyncio
async def test_delete_design_unit_success(
    client: AsyncClient, db_session: AsyncSession
):
    """
    测试场景：删除设计单位成功
    """
    unit = await DesignUnitFactory.create_async(session=db_session)
    response = await client.delete(f"/api/design_unit/{unit.id}")
    assert_api_success(response)
