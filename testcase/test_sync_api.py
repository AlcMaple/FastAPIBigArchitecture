"""
根目录下运行：python -m pytest testcase/test_sync_api.py -v

-m：将当前目录添加到 sys.path 中，目的是找到 app 模块
"""

from fastapi.testclient import TestClient


def test_doctorlist(client: TestClient):
    res = client.get("/api/v1/doctor_list")
    print(
        "sdsd", res.text
    )  # 返回 HTTP 响应体的原始文本，即完整的 JSON 字符串数据，相当于直接返回 res
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_doctorinfo(client: TestClient):
    res = client.get("/api/v1/doctors")
    print("dsdsd", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_doctor_detail(client: TestClient):
    res = client.get("/api/v1/doctor/1")
    print("doctor detail", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_doctors_by_department(client: TestClient):
    res = client.get("/api/v1/doctors/department/内科")
    print("doctors by department", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_create_doctor(client: TestClient):
    doctor_data = {
        "name": "测试医生",
        "department": "内科",
        "title": "主治医师",
        "phone": "13800138001",
        "email": "test@example.com",
    }
    res = client.post("/api/v1/doctor", json=doctor_data)
    print("create doctor", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_doctor_schedules(client: TestClient):
    res = client.get("/api/v1/doctor/1/schedules")
    print("doctor schedules", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_doctor_appointments(client: TestClient):
    res = client.get("/api/v1/doctor/1/appointments")
    print("doctor appointments", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_create_appointment(client: TestClient):
    appointment_data = {
        "doctor_id": 1,
        "patient_name": "测试患者",
        "patient_phone": "13900139001",
        "appointment_date": "2024-12-01",
        "appointment_time": "09:00",
    }
    res = client.post("/api/v1/appointment", json=appointment_data)
    print("create appointment", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_check_appointment_availability(client: TestClient):
    res = client.post(
        "/api/v1/appointment/check",
        json={"doctor_id": 1, "appointment_date": "2024-12-01"},
    )
    print("check appointment", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_appointment_detail(client: TestClient):
    res = client.get("/api/v1/appointment/1")
    print("appointment detail", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_patient_appointments(client: TestClient):
    res = client.get("/api/v1/appointments/patient/13900139001")
    print("patient appointments", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_cancel_appointment(client: TestClient):
    res = client.delete("/api/v1/appointment/1")
    print("cancel appointment", res.text)
    assert res.status_code == 200
    assert type(res.status_code) == int
