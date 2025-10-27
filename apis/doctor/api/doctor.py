from fastapi import Depends, Query, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.doctor import DoctorService
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from exts.responses.api_response import Success
from . import router_doctor
from ..schemas.doctor import DoctorCreateRequest, DoctorUpdateRequest


@router_doctor.get("/doctor_list", summary="获取可以预约的医生列表信息")
async def get_doctor_list(db_session: AsyncSession = Depends(depends_get_db_session)):
    """
    获取可以预约的医生列表信息

    :param db_session: 数据库连接依赖注入对象
    :return: 返回可以预约的医生列表信息
    """
    info = await DoctorService.get_doctor_list_infos(db_session)
    return Success(data=info)


@router_doctor.post(
    "/doctor/{doctor_id}/upload-document", summary="上传医生相关文档或图片"
)
async def upload_doctor_document(
    doctor_id: int = Path(..., description="医生ID"),
    file: UploadFile = File(..., description="上传的文件"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    上传医生相关文档或图片（不保存到数据库）

    :param doctor_id: 医生ID
    :param file: 上传的文件
    :param db_session: 数据库连接依赖注入对象
    :return: 上传结果和文件路径
    """
    data = await DoctorService.upload_doctor_document(db_session, doctor_id, file)
    return Success(data=data, message="文件上传成功")


@router_doctor.post("/doctor/{doctor_id}/upload-avatar", summary="上传医生头像")
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
    data = await DoctorService.upload_doctor_avatar(db_session, doctor_id, avatar)
    return Success(data=data, message="头像上传成功")


@router_doctor.get("/doctor/{doctor_id}/avatar", summary="获取医生头像信息")
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
    data = await DoctorService.get_doctor_avatar(db_session, doctor_id)
    return Success(data=data)
