from fastapi import Path

from ..services.doctor import DoctorService
from exts.responses.json_response import Success, Fail
from . import router_doctor
from ..schemas.doctor import DoctorCreateRequest, DoctorUpdateRequest


@router_doctor.get("/doctors", summary="获取所有医生列表信息")
async def get_all_doctors():
    """
    获取所有医生列表信息

    :return: 返回所有医生列表信息
    """
    try:
        info = await DoctorService.get_all_doctors()
        return Success(result=info)
    except Exception as e:
        return Fail(message=f"获取医生列表失败: {str(e)}")


@router_doctor.get("/doctor/{doctor_id}", summary="获取医生详细信息")
async def get_doctor_detail(doctor_id: int = Path(..., description="医生ID")):
    """
    获取医生详细信息

    :param doctor_id: 医生ID
    :return: 返回医生详细信息
    """
    try:
        doctor_info = await DoctorService.get_doctor_detail(doctor_id)
        if not doctor_info:
            return Fail(message="医生信息不存在", api_code=404)

        return Success(result=doctor_info)
    except Exception as e:
        return Fail(message=f"获取医生信息失败: {str(e)}")


@router_doctor.post("/doctor", summary="创建医生")
async def create_doctor(doctor_request: DoctorCreateRequest):
    """
    创建医生

    :param doctor_request: 创建医生请求
    :return: 创建的医生信息
    """
    try:
        result = await DoctorService.create_doctor(doctor_request)
        return Success(result=result, message="医生创建成功")
    except ValueError as e:
        return Fail(message=str(e))
    except Exception as e:
        return Fail(message=f"创建医生失败: {str(e)}")


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
    try:
        result = await DoctorService.update_doctor(doctor_id, doctor_request)
        return Success(result=result, message="医生信息更新成功")
    except ValueError as e:
        return Fail(message=str(e), api_code=404 if "不存在" in str(e) else 400)
    except Exception as e:
        return Fail(message=f"更新医生信息失败: {str(e)}")


@router_doctor.delete("/doctor/{doctor_id}", summary="删除医生")
async def delete_doctor(doctor_id: int = Path(..., description="医生ID")):
    """
    删除医生

    :param doctor_id: 医生ID
    :return: 删除结果
    """
    try:
        success = await DoctorService.delete_doctor(doctor_id)
        return Success(result={"deleted": success}, message="医生删除成功")
    except ValueError as e:
        return Fail(message=str(e), api_code=404 if "不存在" in str(e) else 400)
    except Exception as e:
        return Fail(message=f"删除医生失败: {str(e)}")
