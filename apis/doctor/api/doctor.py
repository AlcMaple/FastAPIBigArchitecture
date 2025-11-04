from fastapi import Path, UploadFile, File
from datetime import date

from ..services.doctor import DoctorService
from exts.responses.api_response import Success
from . import router_doctor
from ..schemas.doctor import (
    DoctorCreateRequest,
    DoctorUpdateRequest,
)


@router_doctor.get("/doctors", summary="获取所有医生列表信息")
async def get_all_doctors():
    """
    获取所有医生列表信息

    :return: 返回所有医生列表信息
    """
    info = await DoctorService.get_all_doctors()
    return Success(data=info.model_dump())


@router_doctor.get("/doctor/{doctor_id}", summary="获取医生详细信息")
async def get_doctor_detail(doctor_id: int = Path(..., description="医生ID")):
    """
    获取医生详细信息

    :param doctor_id: 医生ID
    :return: 返回医生详细信息
    """
    doctor_info = await DoctorService.get_doctor_detail(doctor_id)
    return Success(data=doctor_info.model_dump())


@router_doctor.post("/doctor", summary="创建医生")
async def create_doctor(doctor_request: DoctorCreateRequest):
    """
    创建医生

    :param doctor_request: 创建医生请求
    :return: 创建的医生信息
    """
    result = await DoctorService.create_doctor(doctor_request)
    return Success(data=result.model_dump(), message="医生创建成功")


@router_doctor.put("/doctor/{doctor_id}", summary="更新医生信息")
async def update_doctor(
    doctor_id: int = Path(..., description="医生ID"),
    doctor_request: DoctorUpdateRequest = None,
):
    """
    更新医生信息

    :param doctor_id: 医生ID
    :param doctor_request: 更新医生请求
    :return: 更新后的医生信息
    """
    result = await DoctorService.update_doctor(doctor_id, doctor_request)
    return Success(data=result.model_dump(), message="医生信息更新成功")


@router_doctor.delete("/doctor/{doctor_id}", summary="删除医生")
async def delete_doctor(doctor_id: int = Path(..., description="医生ID")):
    """
    删除医生

    :param doctor_id: 医生ID
    :return: 删除结果
    """
    result = await DoctorService.delete_doctor(doctor_id)
    return Success(data=result.model_dump(), message="医生删除成功")


@router_doctor.post("/doctor/{doctor_id}/avatar", summary="上传医生头像")
async def upload_doctor_avatar(
    doctor_id: int = Path(..., description="医生ID"),
    avatar: UploadFile = File(..., description="医生头像文件"),
):
    """
    上传医生头像

    :param doctor_id: 医生ID
    :param avatar: 头像文件
    :return: 上传结果
    """
    result = await DoctorService.upload_doctor_avatar(doctor_id, avatar)
    return Success(data=result.model_dump(), message="头像上传成功")


@router_doctor.get("/doctor/experience/{hire_date}", summary="计算工作经验")
async def calculate_work_experience(
    hire_date: date = Path(..., description="入职日期 (格式: YYYY-MM-DD)")
):
    """
    计算医生工作经验

    :param hire_date: 入职日期
    :return: 工作经验信息
    """
    result = await DoctorService.calculate_work_experience(hire_date)
    return Success(data=result.model_dump(), message="工作经验计算成功")
