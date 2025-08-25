"""
异步测试用例文件

运行命令：
python -m pytest testcase/test_api.py -v

或者运行异步测试：
python -m pytest testcase/test_api.py -v --asyncio-mode=auto

-m：将当前目录添加到 sys.path 中，目的是找到 app 模块
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession


# 保留同步测试，用于向后兼容
def test_doctorlist_sync(client: TestClient):
    """同步测试：获取医生列表"""
    response = client.get("/api/v1/doctor_list")
    print("同步测试响应:", response.text)
    assert response.status_code == 200
    assert isinstance(response.status_code, int)


def test_doctorinfo_sync(client: TestClient):
    """同步测试：获取医生信息"""
    response = client.get("/api/v1/doctors")
    print("同步测试响应:", response.text)
    assert response.status_code == 200
    assert isinstance(response.status_code, int)


# 异步测试用例 - 推荐使用
@pytest.mark.asyncio
async def test_doctorlist_async(async_client: AsyncClient):
    """异步测试：获取医生列表"""
    response = await async_client.get("/api/v1/doctor_list")
    print("异步测试响应:", response.text)

    assert response.status_code == 200
    assert isinstance(response.status_code, int)

    # 检查响应格式
    json_data = response.json()
    assert "code" in json_data or "message" in json_data or "data" in json_data


@pytest.mark.asyncio
async def test_doctorinfo_async(async_client: AsyncClient):
    """异步测试：获取医生信息"""
    response = await async_client.get("/api/v1/doctors")
    print("异步测试响应:", response.text)

    assert response.status_code == 200
    assert isinstance(response.status_code, int)

    # 检查响应格式
    json_data = response.json()
    assert "code" in json_data or "message" in json_data or "data" in json_data


@pytest.mark.asyncio
async def test_health_check_async(async_client: AsyncClient):
    """异步测试：健康检查"""
    response = await async_client.get("/health")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert "message" in json_data


@pytest.mark.asyncio
async def test_root_endpoint_async(async_client: AsyncClient):
    """异步测试：根路径"""
    response = await async_client.get("/")

    assert response.status_code == 200
    json_data = response.json()
    assert "message" in json_data
    assert json_data["status"] == "healthy"


# 带数据库操作的异步测试示例
@pytest.mark.asyncio
async def test_with_database_async(async_client: AsyncClient, db_session: AsyncSession):
    """异步测试：涉及数据库操作的测试用例示例"""
    # 这里可以直接使用 db_session 进行数据库操作
    # 例如：创建测试数据、验证数据库状态等

    # 测试API端点
    response = await async_client.get("/api/v1/doctor_list")
    assert response.status_code == 200

    # 可以在这里验证数据库状态
    # 例如：检查数据是否正确保存到数据库
    print(f"数据库会话类型: {type(db_session)}")
    print(f"数据库会话状态: {db_session.is_active}")


# 错误处理测试
@pytest.mark.asyncio
async def test_not_found_endpoint_async(async_client: AsyncClient):
    """异步测试：404错误处理"""
    response = await async_client.get("/api/v1/non_existent_endpoint")
    assert response.status_code == 404


# POST请求测试示例
@pytest.mark.asyncio
async def test_post_request_async(async_client: AsyncClient):
    """异步测试：POST请求示例"""
    # 这里是一个POST请求的示例，需要根据实际API调整
    # response = await async_client.post(
    #     "/api/v1/doctors",
    #     json={
    #         "name": "测试医生",
    #         "specialty": "内科",
    #         "phone": "13800138000"
    #     }
    # )
    # assert response.status_code == 201  # 或者200，取决于API设计

    # 暂时跳过，因为没有具体的POST端点
    pytest.skip("需要实际的POST端点来测试")


# 参数化测试示例
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint", ["/", "/health", "/api/v1/doctor_list", "/api/v1/doctors"]
)
async def test_multiple_endpoints_async(async_client: AsyncClient, endpoint: str):
    """异步测试：参数化测试多个端点"""
    response = await async_client.get(endpoint)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


# 并发测试示例
@pytest.mark.asyncio
async def test_concurrent_requests_async(async_client: AsyncClient):
    """异步测试：并发请求测试"""
    import asyncio

    # 同时发送多个请求
    tasks = []
    for i in range(5):
        task = async_client.get("/api/v1/doctor_list")
        tasks.append(task)

    responses = await asyncio.gather(*tasks)

    # 验证所有响应
    for response in responses:
        assert response.status_code == 200
        assert isinstance(response.json(), dict)


class TestDoctorAPI:
    """医生API测试类 - 组织相关测试"""

    @pytest.mark.asyncio
    async def test_doctor_list(self, async_client: AsyncClient):
        """测试获取医生列表"""
        response = await async_client.get("/api/v1/doctor_list")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_doctors_info(self, async_client: AsyncClient):
        """测试获取医生信息"""
        response = await async_client.get("/api/v1/doctors")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_doctor_crud_operations(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """测试医生CRUD操作（需要实际实现后启用）"""
        # 创建医生
        # create_data = {
        #     "name": "测试医生",
        #     "specialty": "心内科",
        #     "phone": "13900139000"
        # }
        # response = await async_client.post("/api/v1/doctors", json=create_data)
        # assert response.status_code == 201
        # doctor_id = response.json()["data"]["id"]

        # 获取医生详情
        # response = await async_client.get(f"/api/v1/doctors/{doctor_id}")
        # assert response.status_code == 200

        # 更新医生信息
        # update_data = {"specialty": "心外科"}
        # response = await async_client.put(f"/api/v1/doctors/{doctor_id}", json=update_data)
        # assert response.status_code == 200

        # 删除医生
        # response = await async_client.delete(f"/api/v1/doctors/{doctor_id}")
        # assert response.status_code == 204

        pytest.skip("需要完整的CRUD端点实现")
