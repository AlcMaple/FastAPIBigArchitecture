from typing import Dict, List, Optional, Any
from datetime import date
from fastapi import UploadFile

from ..repository.doctor import DoctorRepository
from ..schemas.doctor import (
    DoctorCreateRequest,
    DoctorUpdateRequest,
    DoctorAvatarUploadResponse,
)
from exts.logururoute.business_logger import logger
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode
from utils.file import FileUtils
from utils.datetime import diff_days_for_now_time


class DoctorService:
    """医生业务服务层"""

    @staticmethod
    async def get_all_doctors() -> Dict[str, Any]:
        """
        获取所有医生列表信息

        :return: 所有医生列表信息
        """
        all_doctors = await DoctorRepository.get_all_doctors()

        # 计算工作天数
        for doctor in all_doctors:
            if doctor.get("hire_date"):
                doctor["work_days"] = diff_days_for_now_time(doctor["hire_date"]) * -1
            else:
                doctor["work_days"] = None

        return {"doctors": all_doctors, "total": len(all_doctors)}

    @staticmethod
    async def get_doctor_detail(doctor_id: int) -> Optional[Dict[str, Any]]:
        """
        获取医生详细信息

        :param doctor_id: 医生ID
        :return: 医生详细信息
        """
        doctor = await DoctorRepository.get_doctor_by_id(doctor_id)
        if doctor and doctor.get("hire_date"):
            doctor["work_days"] = diff_days_for_now_time(doctor["hire_date"]) * -1

        return doctor

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
            raise ApiException(ErrorCode.MISSING_PARAMETER, "医生姓名不能为空")

        if not doctor_data.get("department"):
            raise ApiException(ErrorCode.MISSING_PARAMETER, "科室不能为空")

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
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # 过滤掉None值
        update_data = {k: v for k, v in doctor_request.dict().items() if v is not None}

        if not update_data:
            raise ApiException(ErrorCode.PARAMETER_ERROR, "没有需要更新的数据")

        # 调用Repository层更新医生
        updated_doctor = await DoctorRepository.update_doctor(doctor_id, update_data)

        if not updated_doctor:
            raise ApiException(ErrorCode.BUSINESS_ERROR, "更新医生信息失败")

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
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # TODO: 这里可以添加业务逻辑检查
        # 例如：检查医生是否有未完成的预约等

        # 调用Repository层删除医生
        success = await DoctorRepository.delete_doctor(doctor_id)

        if not success:
            raise ApiException(ErrorCode.BUSINESS_ERROR, "删除医生失败")

        return success

    @staticmethod
    async def upload_doctor_avatar(
        doctor_id: int, avatar_file: UploadFile
    ) -> Dict[str, Any]:
        """
        上传医生头像

        :param doctor_id: 医生ID
        :param avatar_file: 头像文件
        :return: 上传结果
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        try:
            # 使用FileUtils保存头像文件
            avatar_path = await FileUtils.save_damage_image(avatar_file)

            # 更新医生头像路径
            update_data = {"avatar": avatar_path}
            await DoctorRepository.update_doctor(doctor_id, update_data)

            logger.info(f"医生 {doctor_id} 头像上传成功: {avatar_path}")

            return {"avatar_path": avatar_path, "message": "头像上传成功"}

        except ApiException:
            # 如果是 ApiException，直接向上抛出
            raise
        except Exception as e:
            logger.error(f"医生 {doctor_id} 头像上传异常: {str(e)}")
            raise ApiException(ErrorCode.BUSINESS_ERROR, f"头像上传失败: {str(e)}")

    @staticmethod
    async def calculate_work_experience(hire_date: date) -> Dict[str, Any]:
        """
        计算医生工作经验

        :param hire_date: 入职日期
        :return: 工作经验信息
        """
        if not hire_date:
            raise ApiException(ErrorCode.MISSING_PARAMETER, "入职日期不能为空")

        work_days = diff_days_for_now_time(hire_date) * -1
        work_years = work_days // 365
        remaining_days = work_days % 365

        return {
            "work_days": work_days,
            "work_years": work_years,
            "remaining_days": remaining_days,
            "hire_date": hire_date.isoformat(),
        }
