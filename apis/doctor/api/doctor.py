from fastapi import Depends, Query, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.appointment import AppointmentService
from ..services.doctor import DoctorService
from ..services.schedule import ScheduleService
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from exts.responses.json_response import Success, Fail
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
    return Success(result=info)


@router_doctor.get("/doctors", summary="获取所有医生列表信息")
async def get_all_doctors(db_session: AsyncSession = Depends(depends_get_db_session)):
    """
    获取所有医生列表信息

    :param db_session: 数据库连接依赖注入对象
    :return: 返回所有医生列表信息
    """
    info = await DoctorService.get_all_doctors(db_session)
    return Success(result=info)


@router_doctor.get("/doctor/{doctor_id}", summary="获取医生详细信息")
async def get_doctor_detail(
    doctor_id: int = Path(..., description="医生ID"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    获取医生详细信息

    :param doctor_id: 医生ID
    :param db_session: 数据库连接依赖注入对象
    :return: 返回医生详细信息
    """
    doctor_info = await DoctorService.get_doctor_detail(db_session, doctor_id)

    return Success(result=doctor_info)


@router_doctor.get("/doctors/department/{department}", summary="根据科室获取医生列表")
async def get_doctors_by_department(
    department: str = Path(..., description="科室名称"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    根据科室获取医生列表

    :param department: 科室名称
    :param db_session: 数据库连接依赖注入对象
    :return: 返回该科室的医生列表
    """
    result = await DoctorService.get_doctors_by_department(db_session, department)
    return Success(result=result)


@router_doctor.post("/doctor", summary="创建医生")
async def create_doctor(
    doctor_request: DoctorCreateRequest,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    创建医生

    :param doctor_request: 创建医生请求
    :param db_session: 数据库连接依赖注入对象
    :return: 创建的医生信息
    """
    result = await DoctorService.create_doctor(db_session, doctor_request)
    return Success(result=result, message="医生创建成功")


@router_doctor.put("/doctor/{doctor_id}", summary="更新医生信息")
async def update_doctor(
    doctor_id: int = Path(..., description="医生ID"),
    doctor_request: DoctorUpdateRequest = None,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    更新医生信息

    :param doctor_id: 医生ID
    :param doctor_request: 更新医生请求
    :param db_session: 数据库连接依赖注入对象
    :return: 更新后的医生信息
    """
    result = await DoctorService.update_doctor(db_session, doctor_id, doctor_request)
    return Success(result=result, message="医生信息更新成功")


@router_doctor.delete("/doctor/{doctor_id}", summary="删除医生")
async def delete_doctor(
    doctor_id: int = Path(..., description="医生ID"),
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    删除医生

    :param doctor_id: 医生ID
    :param db_session: 数据库连接依赖注入对象
    :return: 删除结果
    """
    success = await DoctorService.delete_doctor(db_session, doctor_id)
    return Success(result={"deleted": success}, message="医生删除成功")


@router_doctor.get("/doctor/{doctor_id}/schedules", summary="获取医生排班信息")
async def get_doctor_schedules(
    doctor_id: int = Path(..., description="医生ID"),
    days: int = Query(7, description="获取未来几天的排班", ge=1, le=30),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    获取医生排班信息

    :param doctor_id: 医生ID
    :param days: 获取未来几天的排班
    :param db_session: 数据库连接依赖注入对象
    :return: 返回医生排班信息
    """
    schedules = await ScheduleService.get_doctor_schedules(db_session, doctor_id, days)
    return Success(result={"schedules": schedules, "total": len(schedules)})


@router_doctor.get("/doctor/{doctor_id}/appointments", summary="获取医生预约列表")
async def get_doctor_appointments(
    doctor_id: int = Path(..., description="医生ID"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    获取医生预约列表

    :param doctor_id: 医生ID
    :param db_session: 数据库连接依赖注入对象
    :return: 返回医生预约列表
    """
    result = await AppointmentService.get_doctor_appointments(db_session, doctor_id)
    return Success(result=result)


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
    result = await DoctorService.upload_doctor_document(db_session, doctor_id, file)
    return Success(result=result, message="文件上传成功")


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
    result = await DoctorService.upload_doctor_avatar(db_session, doctor_id, avatar)
    return Success(result=result, message="头像上传成功")


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
    result = await DoctorService.get_doctor_avatar(db_session, doctor_id)
    return Success(result=result)
