import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from apis.doctor.services.doctor import DoctorService
from apis.doctor.services.schedule import ScheduleService
from apis.doctor.services.appointment import AppointmentService


class TestDoctorApi:
    """测试医生API"""

    @pytest.mark.asyncio
    async def test_get_doctor_list_success(self, client):
        """测试获取可以预约的医生列表成功"""
        mock_result = [
            {
                "id": 1,
                "name": "测试医生1",
                "department": "内科",
                "title": "主任医师",
                "is_available": True
            },
            {
                "id": 2,
                "name": "测试医生2",
                "department": "外科",
                "title": "副主任医师",
                "is_available": True
            }
        ]

        with patch.object(
            DoctorService, "get_doctor_list_infos", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/doctor_list")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_get_all_doctors_success(self, client):
        """测试获取所有医生列表成功"""
        mock_result = [
            {
                "id": 1,
                "name": "测试医生1",
                "department": "内科",
                "title": "主任医师"
            },
            {
                "id": 2,
                "name": "测试医生2",
                "department": "外科",
                "title": "副主任医师"
            }
        ]

        with patch.object(
            DoctorService, "get_all_doctors", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/doctors")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_get_doctor_detail_success(self, client):
        """测试获取医生详细信息成功"""
        mock_result = {
            "id": 1,
            "name": "测试医生",
            "department": "内科",
            "title": "主任医师",
            "experience": "20年从医经验",
            "specialization": "心血管疾病"
        }

        with patch.object(
            DoctorService, "get_doctor_detail", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/doctor/1")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_get_doctors_by_department_success(self, client):
        """测试根据科室获取医生列表成功"""
        mock_result = [
            {
                "id": 1,
                "name": "测试医生1",
                "department": "内科",
                "title": "主任医师"
            },
            {
                "id": 3,
                "name": "测试医生3",
                "department": "内科",
                "title": "主治医师"
            }
        ]

        with patch.object(
            DoctorService, "get_doctors_by_department", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/doctors/department/内科")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_create_doctor_success(self, client):
        """测试创建医生成功"""
        doctor_data = {
            "name": "新医生",
            "department": "内科",
            "title": "主治医师",
            "specialty": "心血管疾病"
        }

        mock_result = {
            "id": 3,
            "name": "新医生",
            "department": "内科",
            "title": "主治医师",
            "phone": "13800138001",
            "is_active": True
        }

        with patch.object(
            DoctorService, "create_doctor", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.post("/api/v1/doctor", json=doctor_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "医生创建成功"
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_update_doctor_success(self, client):
        """测试更新医生信息成功"""
        update_data = {
            "name": "更新医生",
            "title": "副主任医师"
        }

        mock_result = {
            "id": 1,
            "name": "更新医生",
            "department": "内科",
            "title": "副主任医师",
            "phone": "13800138001"
        }

        with patch.object(
            DoctorService, "update_doctor", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.put("/api/v1/doctor/1", json=update_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "医生信息更新成功"
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_delete_doctor_success(self, client):
        """测试删除医生成功"""
        mock_result = True

        with patch.object(
            DoctorService, "delete_doctor", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.delete("/api/v1/doctor/1")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "医生删除成功"
            assert data["result"] == {"deleted": True}

    @pytest.mark.asyncio
    async def test_get_doctor_schedules_success(self, client):
        """测试获取医生排班信息成功"""
        mock_result = [
            {
                "date": "2024-01-01",
                "time_slots": ["09:00", "10:00", "11:00"],
                "available": True
            },
            {
                "date": "2024-01-02",
                "time_slots": ["14:00", "15:00", "16:00"],
                "available": True
            }
        ]

        with patch.object(
            ScheduleService, "get_doctor_schedules", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/doctor/1/schedules?days=7")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"]["schedules"] == mock_result
            assert data["result"]["total"] == len(mock_result)

    @pytest.mark.asyncio
    async def test_get_doctor_appointments_success(self, client):
        """测试获取医生预约列表成功"""
        mock_result = [
            {
                "id": 1,
                "patient_name": "患者1",
                "patient_phone": "13800138000",
                "appointment_date": "2024-01-01T10:00:00",
                "status": "confirmed"
            },
            {
                "id": 2,
                "patient_name": "患者2",
                "patient_phone": "13800138002",
                "appointment_date": "2024-01-02T14:00:00",
                "status": "pending"
            }
        ]

        with patch.object(
            AppointmentService, "get_doctor_appointments", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/doctor/1/appointments")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result