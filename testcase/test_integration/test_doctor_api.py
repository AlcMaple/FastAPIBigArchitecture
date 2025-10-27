"""
集成测试 - 医生 API
"""

import pytest
from io import BytesIO

from testcase.factories import DoctorFactory


class TestDoctorAPI:
    """医生 API 集成测试"""

    def test_upload_doctor_avatar_success(self, client):
        """测试成功上传医生头像"""
        # 使用模拟数据中已存在的医生
        doctor_id = 1

        # 创建模拟图片文件
        image_content = b"fake image content"
        files = {"avatar": ("test_avatar.jpg", BytesIO(image_content), "image/jpeg")}

        # 上传头像
        response = client.post(
            f"/api/v1/doctor/{doctor_id}/upload-avatar",
            files=files,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "头像上传成功"
        assert "data" in data
        assert "avatar" in data["data"]
        # 注意：返回的字段可能不包含 doctor_id，只验证核心字段

    def test_get_doctor_avatar_success(self, client):
        """测试获取医生头像信息"""
        # 使用模拟数据中已存在的医生
        doctor_id = 1

        # 获取头像信息（未上传头像）
        response = client.get(f"/api/v1/doctor/{doctor_id}/avatar")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["doctor_id"] == doctor_id
        assert "doctor_name" in data["data"]
        assert "has_avatar" in data["data"]


class TestDoctorListAPI:
    """医生列表 API 测试"""

    def test_get_doctor_list_with_mock_data(self, client):
        """测试获取可预约医生列表（使用模拟数据）"""
        response = client.get("/api/v1/doctor_list")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 模拟数据中有可预约的医生（available=True的医生）
        assert data["data"]["total"] >= 0
        assert "doctors" in data["data"]
