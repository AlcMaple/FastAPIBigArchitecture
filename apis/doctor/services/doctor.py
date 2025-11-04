from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from fastapi import UploadFile

from ..repository.doctor import DoctorRepository
from ..schemas.doctor import (
    DoctorCreateRequest,
    DoctorUpdateRequest,
    DoctorDetailResponse,
    DoctorListItemResponse,
    DoctorListResponse,
    DoctorAvatarResponse,
    FileUploadResponse,
)
from exts.logururoute.business_logger import logger
from utils.file import FileUtils, FileCategory
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode
from config.settings import settings


class DoctorService:
    """医生业务服务层"""

    @staticmethod
    async def get_doctor_list_infos(
        db_session: AsyncSession, page: int = 1, page_size: int = 10
    ) -> DoctorListResponse:
        """
        获取可以预约的医生列表信息

        :param db_session: 数据库会话对象
        :param page: 页码
        :param page_size: 每页数量
        :return: DoctorListResponse Pydantic 对象
        """
        logger.info("开始获取可预约医生列表")

        # 获取可预约医生列表
        available_doctors = await DoctorRepository.get_available_doctors(db_session)

        doctor_items = []
        for doctor_dict in available_doctors:
            # 生成头像 URL
            avatar_url = None
            if doctor_dict.get("avatar"):
                avatar_url = f"{settings.BASE_URL}/static/{doctor_dict['avatar']}"
            doctor_dict["avatar_url"] = avatar_url
            doctor_items.append(DoctorListItemResponse(**doctor_dict))

        logger.info(f"获取可预约医生列表成功，共{len(doctor_items)}位医生")
        return DoctorListResponse(
            items=doctor_items,
            total=len(doctor_items),
            page=page,
            page_size=page_size,
        )

    @staticmethod
    async def get_all_doctors(db_session: AsyncSession) -> Dict[str, Any]:
        """
        获取所有医生列表信息

        :param db_session: 数据库会话对象
        :return: 所有医生列表信息
        """
        all_doctors = await DoctorRepository.get_all_doctors(db_session)

        return {"doctors": all_doctors, "total": len(all_doctors)}

    @staticmethod
    async def get_doctor_detail(
        db_session: AsyncSession, doctor_id: int
    ) -> DoctorDetailResponse:
        """
        获取医生详细信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: DoctorDetailResponse Pydantic 对象
        :raises ApiException: 医生不存在
        """
        doctor_dict = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor_dict:
            raise ApiException(ErrorCode.NOT_FOUND, f"医生 {doctor_id} 不存在")

        # 生成头像 URL
        avatar_url = None
        if doctor_dict.get("avatar"):
            avatar_url = f"{settings.BASE_URL}/static/{doctor_dict['avatar']}"
        doctor_dict["avatar_url"] = avatar_url

        return DoctorDetailResponse(**doctor_dict)

    @staticmethod
    async def get_doctors_by_department(
        db_session: AsyncSession, department: str
    ) -> Dict[str, Any]:
        """
        根据科室获取医生列表

        :param db_session: 数据库会话对象
        :param department: 科室名称
        :return: 该科室的医生列表
        """
        doctors = await DoctorRepository.get_doctors_by_department(
            db_session, department
        )

        return {"doctors": doctors, "department": department, "total": len(doctors)}

    @staticmethod
    async def create_doctor(
        db_session: AsyncSession, doctor_request: DoctorCreateRequest
    ) -> DoctorDetailResponse:
        """
        创建医生

        :param db_session: 数据库会话对象
        :param doctor_request: 创建医生请求
        :return: DoctorDetailResponse Pydantic 对象（与 get_doctor_detail 返回相同结构）
        :raises ApiException: 业务验证失败
        """
        doctor_data = doctor_request.model_dump()
        if not doctor_data.get("name"):
            raise ApiException(ErrorCode.MISSING_PARAMETER, "医生姓名不能为空")
        if not doctor_data.get("department"):
            raise ApiException(ErrorCode.MISSING_PARAMETER, "科室不能为空")
        new_doctor_dict = await DoctorRepository.create_doctor(db_session, doctor_data)

        # 生成头像 URL
        new_doctor_dict["avatar_url"] = None  # 新创建的医生暂无头像

        return DoctorDetailResponse(**new_doctor_dict)

    @staticmethod
    async def update_doctor(
        db_session: AsyncSession, doctor_id: int, doctor_request: DoctorUpdateRequest
    ) -> DoctorDetailResponse:
        """
        更新医生信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param doctor_request: 更新医生请求
        :return: DoctorDetailResponse Pydantic 对象（与 get_doctor_detail 返回相同结构）
        :raises ApiException: 医生不存在或更新失败
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        update_data = {
            k: v for k, v in doctor_request.model_dump().items() if v is not None
        }
        if not update_data:
            raise ApiException(ErrorCode.PARAMETER_ERROR, "没有需要更新的数据")
        updated_doctor_dict = await DoctorRepository.update_doctor(
            db_session, doctor_id, update_data
        )
        if not updated_doctor_dict:
            raise ApiException(ErrorCode.BUSINESS_ERROR, "更新医生信息失败")

        # 生成头像 URL
        avatar_url = None
        if updated_doctor_dict.get("avatar"):
            avatar_url = f"{settings.BASE_URL}/static/{updated_doctor_dict['avatar']}"
        updated_doctor_dict["avatar_url"] = avatar_url

        return DoctorDetailResponse(**updated_doctor_dict)

    @staticmethod
    async def delete_doctor(db_session: AsyncSession, doctor_id: int) -> bool:
        """
        删除医生

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: 是否删除成功
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # TODO: 这里可以添加业务逻辑检查
        # 例如：检查医生是否有未完成的预约等

        success = await DoctorRepository.delete_doctor(db_session, doctor_id)

        if not success:
            raise ApiException(ErrorCode.BUSINESS_ERROR, "删除医生失败")

        return success

    @staticmethod
    async def upload_doctor_document(
        db_session: AsyncSession, doctor_id: int, file: UploadFile
    ) -> FileUploadResponse:
        """
        上传医生相关文档或图片（不保存到数据库）

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param file: 上传的文件
        :return: FileUploadResponse Pydantic 对象
        :raises ApiException: 医生不存在
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # 保存文件
        file_path = await FileUtils.save_file(file, FileCategory.DOCTOR_DOCUMENT)

        logger.info(f"医生 {doctor_id} 文档上传成功: {file_path}")

        # 获取文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到文件开头

        return FileUploadResponse(
            file_name=file.filename or "unknown",
            file_path=file_path,
            file_url=f"{settings.BASE_URL}/static/{file_path}",
            file_size=file_size,
        )

    @staticmethod
    async def upload_doctor_avatar(
        db_session: AsyncSession, doctor_id: int, avatar_file: UploadFile
    ) -> DoctorAvatarResponse:
        """
        上传医生头像并保存到数据库

        实际项目中应该：
        1. 验证文件格式（仅支持图片）
        2. 检查文件大小限制
        3. 保存文件到指定目录
        4. 更新数据库中医生的头像字段
        5. 删除旧头像文件（如果存在）

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param avatar_file: 上传的头像文件
        :return: DoctorAvatarResponse Pydantic 对象
        :raises ApiException: 上传失败
        """
        try:
            result_dict = await DoctorRepository.upload_doctor_avatar(
                db_session, doctor_id, avatar_file
            )
            logger.info(f"医生 {doctor_id} 头像上传成功: {result_dict['avatar']}")

            # 生成头像 URL
            avatar_url = None
            if result_dict.get("avatar"):
                avatar_url = f"{settings.BASE_URL}/static/{result_dict['avatar']}"

            return DoctorAvatarResponse(
                doctor_id=doctor_id,
                avatar=result_dict.get("avatar"),
                avatar_url=avatar_url,
            )

        except ValueError as e:
            logger.error(f"医生 {doctor_id} 头像上传失败: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"医生 {doctor_id} 头像上传出现未知错误: {str(e)}")
            raise ApiException(ErrorCode.BUSINESS_ERROR, "头像上传失败，请稍后重试")

    @staticmethod
    async def get_doctor_avatar(
        db_session: AsyncSession, doctor_id: int
    ) -> DoctorAvatarResponse:
        """
        获取医生头像信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: DoctorAvatarResponse Pydantic 对象
        :raises ApiException: 医生不存在
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # 获取头像路径
        avatar_path = await DoctorRepository.get_doctor_avatar(db_session, doctor_id)

        # 生成头像 URL
        avatar_url = None
        if avatar_path:
            avatar_url = f"{settings.BASE_URL}/static/{avatar_path}"

        return DoctorAvatarResponse(
            doctor_id=doctor_id,
            avatar=avatar_path,
            avatar_url=avatar_url,
        )
