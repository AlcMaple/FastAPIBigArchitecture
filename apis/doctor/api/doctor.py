from fastapi import Depends, Query, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.doctor import DoctorService
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from exts.responses.api_response import Success
from . import router_doctor
from ..schemas.doctor import (
    DoctorCreateRequest,
    DoctorUpdateRequest,
    DoctorDetailResponse,
    DoctorListResponse,
    DoctorAvatarResponse,
    FileUploadResponse,
)


@router_doctor.get(
    "/doctor_list",
    response_model=DoctorListResponse,
    summary="获取可以预约的医生列表信息",
)
async def get_doctor_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    获取可以预约的医生列表信息（分页）

    :param page: 页码
    :param page_size: 每页数量
    :param db_session: 数据库连接依赖注入对象
    :return: 医生列表响应（包含分页信息）
    """
    result = await DoctorService.get_doctor_list_infos(db_session, page, page_size)
    return Success(data=result.model_dump())


@router_doctor.post(
    "/doctor/{doctor_id}/upload-document",
    response_model=FileUploadResponse,
    summary="上传医生相关文档或图片",
)
async def upload_doctor_document(
    doctor_id: int = Path(..., description="医生ID"),
    file: UploadFile = File(..., description="上传的文件"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    上传医生相关文档（不保存到数据库）

    :param doctor_id: 医生ID
    :param file: 上传的文件
    :param db_session: 数据库连接依赖注入对象
    :return: 上传结果和文件路径
    """
    result = await DoctorService.upload_doctor_document(db_session, doctor_id, file)
    return Success(data=result.model_dump(), message="文件上传成功")


@router_doctor.post(
    "/doctor/{doctor_id}/upload-avatar",
    response_model=DoctorAvatarResponse,
    summary="上传医生头像",
)
async def upload_doctor_avatar(
    doctor_id: int = Path(..., description="医生ID"),
    avatar: UploadFile = File(..., description="头像图片文件"),
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    上传医生头像并保存到数据库

    实际项目中会：
    1. 验证图片格式（仅支持 JPEG、PNG）
    2. 检查文件大小（最大5MB）
    3. 保存图片到 static/uploads/damage_images/ 目录
    4. 更新数据库中医生的头像字段
    5. 返回头像相对路径用于前端显示

    :param doctor_id: 医生ID
    :param avatar: 头像图片文件
    :param db_session: 数据库连接依赖注入对象
    :return: 头像上传结果
    """
    result = await DoctorService.upload_doctor_avatar(db_session, doctor_id, avatar)
    return Success(data=result.model_dump(), message="头像上传成功")


@router_doctor.get(
    "/doctor/{doctor_id}/avatar",
    response_model=DoctorAvatarResponse,
    summary="获取医生头像信息",
)
async def get_doctor_avatar(
    doctor_id: int = Path(..., description="医生ID"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    获取医生头像信息

    :param doctor_id: 医生ID
    :param db_session: 数据库连接依赖注入对象
    :return: 医生头像信息
    """
    result = await DoctorService.get_doctor_avatar(db_session, doctor_id)
    return Success(data=result.model_dump())


@router_doctor.get(
    "/doctor/{doctor_id}",
    response_model=DoctorDetailResponse,
    summary="获取医生详情",
)
async def get_doctor_detail(
    doctor_id: int = Path(..., description="医生ID"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    获取医生详细信息

    :param doctor_id: 医生ID
    :param db_session: 数据库连接依赖注入对象
    :return: 医生详细信息
    """
    doctor = await DoctorService.get_doctor_detail(db_session, doctor_id)
    return Success(data=doctor.model_dump())


@router_doctor.post(
    "/doctor",
    response_model=DoctorDetailResponse,
    summary="创建医生",
)
async def create_doctor(
    doctor_data: DoctorCreateRequest,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    创建医生

    - 创建成功后返回完整的医生信息
    - 返回结构与 GET /doctor/{doctor_id} 一致

    :param doctor_data: 创建医生请求数据
    :param db_session: 数据库连接依赖注入对象
    :return: 创建的医生详细信息
    """
    doctor = await DoctorService.create_doctor(db_session, doctor_data)
    return Success(data=doctor.model_dump(), message="医生创建成功")


@router_doctor.put(
    "/doctor/{doctor_id}",
    response_model=DoctorDetailResponse,
    summary="更新医生信息",
)
async def update_doctor(
    doctor_id: int = Path(..., description="医生ID"),
    doctor_data: DoctorUpdateRequest = ...,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    更新医生信息

    - 更新成功后返回完整的医生信息
    - 返回结构与 GET /doctor/{doctor_id} 一致

    :param doctor_id: 医生ID
    :param doctor_data: 更新医生请求数据
    :param db_session: 数据库连接依赖注入对象
    :return: 更新后的医生详细信息
    """
    doctor = await DoctorService.update_doctor(db_session, doctor_id, doctor_data)
    return Success(data=doctor.model_dump(), message="医生信息更新成功")
