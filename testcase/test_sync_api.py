"""
根目录下运行：pytest testcase/test_sync_api.py -v
"""
import pytest


@pytest.mark.asyncio
async def test_setup_test_data(test_json_db):
    """设置测试数据"""
    # 创建测试医生数据
    test_doctor = {
        "name": "测试医生",
        "department": "内科", 
        "title": "主治医师",
        "specialty": "心血管疾病",
        "available": True
    }
    await test_json_db.create("doctors", test_doctor)


def test_get_doctors_list(client):
    """测试获取医生列表"""
    res = client.get("/api/v1/doctors")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 200
    assert "result" in data
    assert "doctors" in data["result"]
    assert "total" in data["result"]


def test_get_doctor_detail(client):
    """测试获取医生详细信息"""
    # 先创建一个医生
    doctor_data = {
        "name": "测试医生详情",
        "department": "外科",
        "title": "副主任医师",
        "specialty": "骨科手术",
    }
    create_res = client.post("/api/v1/doctor", json=doctor_data)
    assert create_res.status_code == 200
    
    created_doctor = create_res.json()["result"]
    doctor_id = created_doctor["id"]
    
    # 获取医生详情
    res = client.get(f"/api/v1/doctor/{doctor_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 200
    assert data["result"]["name"] == "测试医生详情"


def test_create_doctor(client):
    """测试创建医生"""
    doctor_data = {
        "name": "新建测试医生",
        "department": "儿科",
        "title": "主治医师",
        "specialty": "儿童常见病诊治",
    }
    res = client.post("/api/v1/doctor", json=doctor_data)
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 200
    assert data["result"]["name"] == "新建测试医生"
    assert data["result"]["department"] == "儿科"
    assert "id" in data["result"]


def test_update_doctor(client):
    """测试更新医生信息"""
    # 先创建一个医生
    doctor_data = {
        "name": "待更新医生",
        "department": "内科",
        "title": "医师",
        "specialty": "内科疾病",
    }
    create_res = client.post("/api/v1/doctor", json=doctor_data)
    doctor_id = create_res.json()["result"]["id"]
    
    # 更新医生信息
    update_data = {
        "title": "主治医师",
        "specialty": "心血管疾病专科",
        "available": False
    }
    res = client.put(f"/api/v1/doctor/{doctor_id}", json=update_data)
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 200
    assert data["result"]["title"] == "主治医师"
    assert data["result"]["specialty"] == "心血管疾病专科"
    assert data["result"]["available"] == False


def test_delete_doctor(client):
    """测试删除医生"""
    # 先创建一个医生
    doctor_data = {
        "name": "待删除医生",
        "department": "急诊科",
        "title": "医师",
        "specialty": "急诊医学",
    }
    create_res = client.post("/api/v1/doctor", json=doctor_data)
    doctor_id = create_res.json()["result"]["id"]
    
    # 删除医生
    res = client.delete(f"/api/v1/doctor/{doctor_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 200
    assert data["result"]["deleted"] == True
    
    # 验证医生已被删除
    get_res = client.get(f"/api/v1/doctor/{doctor_id}")
    assert get_res.status_code == 200
    assert get_res.json()["code"] == 404  # 医生不存在


def test_get_nonexistent_doctor(client):
    """测试获取不存在的医生"""
    res = client.get("/api/v1/doctor/99999")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 404  # 医生信息不存在


def test_create_doctor_with_invalid_data(client):
    """测试使用无效数据创建医生"""
    # 缺少必填字段
    invalid_data = {
        "name": "",  # 姓名为空
        "department": "内科",
        "title": "医师",
        "specialty": "内科疾病",
    }
    res = client.post("/api/v1/doctor", json=invalid_data)
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 1000  # 参数异常错误
