"""
设计单位接口黑盒集成测试

运行方式:
    pytest tests/test_example.py -v

前提: 确保应用已启动，或使用 TestClient 内嵌运行
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app import app

BASE_URL = "http://test"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as c:
        yield c


async def test_create_design_unit(client: AsyncClient):
    """正常创建设计单位"""
    payload = {
        "name": "测试设计院",
        "tel": "13800138000",
        "email": "test@example.com",
        "address": "北京市朝阳区",
        "contact": "张三",
    }
    resp = await client.post("/api/design_unit", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == payload["name"]
    assert body["data"]["id"] is not None


async def test_create_design_unit_duplicate(client: AsyncClient):
    """创建重复名称的设计单位应返回 409"""
    payload = {"name": "重复设计院"}
    await client.post("/api/design_unit", json=payload)
    resp = await client.post("/api/design_unit", json=payload)
    assert resp.status_code == 409
    body = resp.json()
    assert body["success"] is False


async def test_get_design_unit(client: AsyncClient):
    """获取已创建的设计单位详情"""
    create_resp = await client.post("/api/design_unit", json={"name": "详情测试院"})
    unit_id = create_resp.json()["data"]["id"]

    resp = await client.get(f"/api/design_unit/{unit_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["id"] == unit_id


async def test_get_design_unit_not_found(client: AsyncClient):
    """获取不存在的设计单位应返回 404"""
    resp = await client.get("/api/design_unit/999999")
    assert resp.status_code == 404
    assert resp.json()["success"] is False


async def test_get_design_units_list(client: AsyncClient):
    """获取设计单位列表"""
    for i in range(3):
        await client.post("/api/design_unit", json={"name": f"列表测试院{i}"})

    resp = await client.get("/api/design_units?page=1&page_size=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


async def test_update_design_unit(client: AsyncClient):
    """更新设计单位"""
    create_resp = await client.post("/api/design_unit", json={"name": "更新前"})
    unit_id = create_resp.json()["data"]["id"]

    resp = await client.put(f"/api/design_unit/{unit_id}", json={"name": "更新后"})
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "更新后"


async def test_delete_design_unit(client: AsyncClient):
    """删除设计单位"""
    create_resp = await client.post("/api/design_unit", json={"name": "待删除院"})
    unit_id = create_resp.json()["data"]["id"]

    resp = await client.delete(f"/api/design_unit/{unit_id}")
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    # 确认已删除
    resp = await client.get(f"/api/design_unit/{unit_id}")
    assert resp.status_code == 404


async def test_validation_error(client: AsyncClient):
    """非法参数应返回 400"""
    payload = {"name": "格式错误院", "email": "not-an-email"}
    resp = await client.post("/api/design_unit", json=payload)
    assert resp.status_code == 400
    assert resp.json()["success"] is False
