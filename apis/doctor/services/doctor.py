from typing import Dict, List, Optional, Any

from ..repository.doctor import DoctorRepository
from ..schemas.doctor import DoctorCreateRequest, DoctorUpdateRequest
from exts.logururoute.business_logger import logger


class DoctorService:
    """医生业务服务层"""

    @staticmethod
    async def get_all_doctors() -> Dict[str, Any]:
        """
        获取所有医生列表信息

        :return: 所有医生列表信息
        """
        all_doctors = await DoctorRepository.get_all_doctors()

        return {"doctors": all_doctors, "total": len(all_doctors)}

    @staticmethod
    async def get_doctor_detail(doctor_id: int) -> Optional[Dict[str, Any]]:
        """
        获取医生详细信息

        :param doctor_id: 医生ID
        :return: 医生详细信息
        """
        return await DoctorRepository.get_doctor_by_id(doctor_id)

    @staticmethod
    async def create_doctor(doctor_request: DoctorCreateRequest) -> Dict[str, Any]:
        """
        创建医生

        :param doctor_request: 创建医生请求
        :return: 创建的医生信息
        """
        # 转换为字典
        doctor_data = doctor_request.dict()

        # 业务逻辑验证
        if not doctor_data.get("name"):
            raise ValueError("医生姓名不能为空")

        if not doctor_data.get("department"):
            raise ValueError("科室不能为空")

        # 调用Repository层创建医生
        new_doctor = await DoctorRepository.create_doctor(doctor_data)

        return new_doctor

    @staticmethod
    async def update_doctor(
        doctor_id: int, doctor_request: DoctorUpdateRequest
    ) -> Dict[str, Any]:
        """
        更新医生信息

        :param doctor_id: 医生ID
        :param doctor_request: 更新医生请求
        :return: 更新后的医生信息
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(doctor_id)
        if not doctor:
            raise ValueError("医生信息不存在")

        # 过滤掉None值
        update_data = {k: v for k, v in doctor_request.dict().items() if v is not None}

        if not update_data:
            raise ValueError("没有需要更新的数据")

        # 调用Repository层更新医生
        updated_doctor = await DoctorRepository.update_doctor(doctor_id, update_data)

        if not updated_doctor:
            raise ValueError("更新医生信息失败")

        return updated_doctor

    @staticmethod
    async def delete_doctor(doctor_id: int) -> bool:
        """
        删除医生

        :param doctor_id: 医生ID
        :return: 是否删除成功
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(doctor_id)
        if not doctor:
            raise ValueError("医生信息不存在")

        # TODO: 这里可以添加业务逻辑检查
        # 例如：检查医生是否有未完成的预约等

        # 调用Repository层删除医生
        success = await DoctorRepository.delete_doctor(doctor_id)

        if not success:
            raise ValueError("删除医生失败")

        return success
