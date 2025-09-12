import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from apis.doctor.services.appointment import AppointmentService
from apis.doctor.services.schedule import ScheduleService


class TestAppointmentApi:
    """测试预约API"""

    @pytest.mark.asyncio
    async def test_create_appointment_success(self, client):
        """测试成功创建预约"""
        appointment_data = {
            "doctor_id": 1,
            "patient_name": "测试患者",
            "phone": "13800138000",
            "appointment_date": "2024-01-01T10:00:00"
        }

        mock_result = {
            "id": 1,
            "doctor_id": 1,
            "patient_name": "测试患者",
            "patient_phone": "13800138000",
            "appointment_date": "2024-01-01T10:00:00",
            "status": "pending"
        }

        with patch.object(
            AppointmentService, "create_appointment", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.post("/api/v1/appointment", json=appointment_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "预约成功"
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_check_appointment_availability_success(self, client):
        """测试检查预约可用性成功"""
        mock_result = {
            "available": True,
            "available_slots": ["09:00", "10:00", "11:00"]
        }

        with patch.object(
            ScheduleService, "check_schedule_availability", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.post(
                "/api/v1/appointment/check",
                params={
                    "doctor_id": 1,
                    "appointment_date": "2024-01-01"
                }
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_get_appointment_detail_success(self, client):
        """测试获取预约详情成功"""
        mock_result = {
            "id": 1,
            "doctor_id": 1,
            "patient_name": "测试患者",
            "patient_phone": "13800138000",
            "appointment_date": "2024-01-01T10:00:00",
            "status": "confirmed"
        }

        with patch.object(
            AppointmentService, "get_appointment_detail", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/appointment/1")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result

    @pytest.mark.asyncio
    async def test_cancel_appointment_success(self, client):
        """测试取消预约成功"""
        mock_result = True

        with patch.object(
            AppointmentService, "cancel_appointment", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.delete("/api/v1/appointment/1")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "预约取消成功"
            assert data["result"] == {"cancelled": True}

    @pytest.mark.asyncio
    async def test_get_patient_appointments_success(self, client):
        """测试根据患者电话获取预约列表成功"""
        mock_result = [
            {
                "id": 1,
                "doctor_id": 1,
                "patient_name": "测试患者",
                "patient_phone": "13800138000",
                "appointment_date": "2024-01-01T10:00:00",
                "status": "confirmed"
            }
        ]

        with patch.object(
            AppointmentService, "get_patient_appointments", new_callable=AsyncMock
        ) as mock_service:
            mock_service.return_value = mock_result

            response = client.get("/api/v1/appointments/patient/13800138000")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["result"] == mock_result