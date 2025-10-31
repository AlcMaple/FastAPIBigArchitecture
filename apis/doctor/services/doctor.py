from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from fastapi import UploadFile

from ..repository.doctor import DoctorRepository
from ..schemas.doctor import DoctorCreateRequest, DoctorUpdateRequest
from exts.logururoute.business_logger import logger
from utils.file import FileUtils, FileCategory
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode


class DoctorService:
    """医生业务服务层"""

    @staticmethod
    async def get_doctor_list_infos(db_session: AsyncSession) -> Dict[str, Any]:
        """
        获取可以预约的医生列表信息

        :param db_session: 数据库会话对象
        :return: 医生列表信息
        """
        logger.info("开始获取可预约医生列表")
        logger.warning("测试警告")
        logger.error("测试错误")
        logger.debug("测试调试")
        logger.critical("测试严重")

        available_doctors = await DoctorRepository.get_available_doctors(db_session)

        logger.info(f"获取可预约医生列表成功，共{len(available_doctors)}位医生")
        return {"doctors": available_doctors, "total": len(available_doctors)}

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
    ) -> Optional[Dict[str, Any]]:
        """
        获取医生详细信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: 医生详细信息
        """
        return await DoctorRepository.get_doctor_by_id(db_session, doctor_id)

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
    ) -> Dict[str, Any]:
        """
        创建医生

        :param db_session: 数据库会话对象
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
        new_doctor = await DoctorRepository.create_doctor(db_session, doctor_data)

        return new_doctor

    @staticmethod
    async def update_doctor(
        db_session: AsyncSession, doctor_id: int, doctor_request: DoctorUpdateRequest
    ) -> Dict[str, Any]:
        """
        更新医生信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param doctor_request: 更新医生请求
        :return: 更新后的医生信息
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # 过滤掉None值
        update_data = {k: v for k, v in doctor_request.dict().items() if v is not None}

        if not update_data:
            raise ApiException(ErrorCode.PARAMETER_ERROR, "没有需要更新的数据")

        # 调用Repository层更新医生
        updated_doctor = await DoctorRepository.update_doctor(
            db_session, doctor_id, update_data
        )

        if not updated_doctor:
            raise ApiException(ErrorCode.BUSINESS_ERROR, "更新医生信息失败")

        return updated_doctor

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

        # 调用Repository层删除医生
        success = await DoctorRepository.delete_doctor(db_session, doctor_id)

        if not success:
            raise ApiException(ErrorCode.BUSINESS_ERROR, "删除医生失败")

        return success

    @staticmethod
    async def upload_doctor_document(
        db_session: AsyncSession, doctor_id: int, file: UploadFile
    ) -> Dict[str, Any]:
        """
        上传医生相关文档或图片（不保存到数据库）

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param file: 上传的文件
        :return: 文件上传结果
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # 使用FileUtil保存文件
        file_path = await FileUtils.save_file(file, FileCategory.DOCTOR_DOCUMENT)

        logger.info(f"医生 {doctor_id} 文档上传成功: {file_path}")

        return {
            "doctor_id": doctor_id,
            "file_path": file_path,
            "original_filename": file.filename,
            "content_type": file.content_type,
        }

    @staticmethod
    async def upload_doctor_avatar(
        db_session: AsyncSession, doctor_id: int, avatar_file: UploadFile
    ) -> Dict[str, Any]:
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
        :return: 头像上传结果
        """
        try:
            # 调用Repository层处理头像上传和数据库保存
            result = await DoctorRepository.upload_doctor_avatar(
                db_session, doctor_id, avatar_file
            )

            logger.info(f"医生 {doctor_id} 头像上传成功: {result['avatar']}")

            return result

        except ValueError as e:
            logger.error(f"医生 {doctor_id} 头像上传失败: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"医生 {doctor_id} 头像上传出现未知错误: {str(e)}")
            raise ApiException(ErrorCode.BUSINESS_ERROR, "头像上传失败，请稍后重试")

    @staticmethod
    async def get_doctor_avatar(
        db_session: AsyncSession, doctor_id: int
    ) -> Dict[str, Any]:
        """
        获取医生头像信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: 头像信息
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ApiException(ErrorCode.NOT_FOUND, "医生信息不存在")

        # 获取头像路径
        avatar_path = await DoctorRepository.get_doctor_avatar(db_session, doctor_id)

        return {
            "doctor_id": doctor_id,
            "doctor_name": doctor["name"],
            "avatar": avatar_path,
            "has_avatar": avatar_path is not None,
        }
