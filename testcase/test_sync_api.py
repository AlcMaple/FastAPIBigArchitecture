"""
根目录下运行：pytest testcase/test_sync_api.py -v
"""


def test_doctorlist(client):
    res = client.get("/api/v1/doctor_list")
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_doctorinfo(client):
    res = client.get("/api/v1/doctors")
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_doctor_detail(client):
    res = client.get("/api/v1/doctor/1")
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_create_doctor(client):
    doctor_data = {
        "name": "测试医生",
        "department": "内科",
        "title": "主治医师",
        "specialty": "心血管疾病诊治",
    }
    res = client.post("/api/v1/doctor", json=doctor_data)
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_check_appointment_availability(client):
    res = client.post(
        "/api/v1/appointment/check",
        params={"doctor_id": 1, "appointment_date": "2024-12-01"},
    )
    assert res.status_code == 200
    assert type(res.status_code) == int


def test_cancel_appointment(client):
    res = client.delete("/api/v1/appointment/1")
    assert res.status_code == 200
    assert type(res.status_code) == int
