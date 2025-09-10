import pytest
from fastapi.testclient import TestClient

"""
根目录下运行：pytest testcase/test_sync_api.py -v
"""


class TestSyncAPI:

    def test_doctorlist(self, client: TestClient):
        res = client.get("/api/v1/doctor_list")
        assert res.status_code == 200
        assert type(res.status_code) == int

    def test_doctorinfo(self, client: TestClient):
        res = client.get("/api/v1/doctors")
        assert res.status_code == 200
        assert type(res.status_code) == int

    def test_doctor_detail(self, client: TestClient):
        res = client.get("/api/v1/doctor/1")
        assert res.status_code == 200
        assert type(res.status_code) == int

    def test_create_doctor(self, client: TestClient):
        doctor_data = {
            "name": "测试医生",
            "department": "内科",
            "title": "主治医师",
            "specialty": "心血管疾病诊治",
        }
        res = client.post("/api/v1/doctor", json=doctor_data)
        assert res.status_code == 200
        assert type(res.status_code) == int

    def test_check_appointment_availability(self, client: TestClient):
        res = client.post(
            "/api/v1/appointment/check",
            params={"doctor_id": 1, "appointment_date": "2024-12-01"},
        )
        assert res.status_code == 200
        assert type(res.status_code) == int

    def test_cancel_appointment(self, client: TestClient):
        res = client.delete("/api/v1/appointment/1")
        assert res.status_code == 200
        assert type(res.status_code) == int
