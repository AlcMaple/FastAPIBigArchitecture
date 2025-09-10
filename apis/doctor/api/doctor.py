from fastapi import Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.appointment import AppointmentService
from ..services.doctor import DoctorService
from ..services.schedule import ScheduleService
from db.database import depends_get_db_session
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
    try:
        info = await DoctorService.get_doctor_list_infos(db_session)
        return Success(result=info)
    except Exception as e:
        return Fail(message=f"获取医生列表失败: {str(e)}")


@router_doctor.get("/doctors", summary="获取所有医生列表信息")
async def get_all_doctors(db_session: AsyncSession = Depends(depends_get_db_session)):
    """
    获取所有医生列表信息

    :param db_session: 数据库连接依赖注入对象
    :return: 返回所有医生列表信息
    """
    try:
        info = await DoctorService.get_all_doctors(db_session)
        return Success(result=info)
    except Exception as e:
        return Fail(message=f"获取医生列表失败: {str(e)}")


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
    try:
        doctor_info = await DoctorService.get_doctor_detail(db_session, doctor_id)
        if not doctor_info:
            return Fail(message="医生信息不存在", api_code=404)

        return Success(result=doctor_info)
    except Exception as e:
        return Fail(message=f"获取医生信息失败: {str(e)}")


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
    try:
        result = await DoctorService.get_doctors_by_department(db_session, department)
        return Success(result=result)
    except Exception as e:
        return Fail(message=f"获取科室医生列表失败: {str(e)}")


@router_doctor.post("/doctor", summary="创建医生")
async def create_doctor(
    doctor_request: DoctorCreateRequest,
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    创建医生

    :param doctor_request: 创建医生请求
    :param db_session: 数据库连接依赖注入对象
    :return: 创建的医生信息
    """
    try:
        result = await DoctorService.create_doctor(db_session, doctor_request)
        return Success(result=result, message="医生创建成功")
    except ValueError as e:
        return Fail(message=str(e))
    except Exception as e:
        return Fail(message=f"创建医生失败: {str(e)}")


@router_doctor.put("/doctor/{doctor_id}", summary="更新医生信息")
async def update_doctor(
    doctor_id: int = Path(..., description="医生ID"),
    doctor_request: DoctorUpdateRequest = None,
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    更新医生信息

    :param doctor_id: 医生ID
    :param doctor_request: 更新医生请求
    :param db_session: 数据库连接依赖注入对象
    :return: 更新后的医生信息
    """
    try:
        result = await DoctorService.update_doctor(
            db_session, doctor_id, doctor_request
        )
        return Success(result=result, message="医生信息更新成功")
    except ValueError as e:
        return Fail(message=str(e), api_code=404 if "不存在" in str(e) else 400)
    except Exception as e:
        return Fail(message=f"更新医生信息失败: {str(e)}")


@router_doctor.delete("/doctor/{doctor_id}", summary="删除医生")
async def delete_doctor(
    doctor_id: int = Path(..., description="医生ID"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    删除医生

    :param doctor_id: 医生ID
    :param db_session: 数据库连接依赖注入对象
    :return: 删除结果
    """
    try:
        success = await DoctorService.delete_doctor(db_session, doctor_id)
        return Success(result={"deleted": success}, message="医生删除成功")
    except ValueError as e:
        return Fail(message=str(e), api_code=404 if "不存在" in str(e) else 400)
    except Exception as e:
        return Fail(message=f"删除医生失败: {str(e)}")


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
    try:
        schedules = await ScheduleService.get_doctor_schedules(
            db_session, doctor_id, days
        )
        if not schedules:
            return Fail(message="医生信息不存在或暂无排班", api_code=404)

        return Success(result={"schedules": schedules, "total": len(schedules)})
    except Exception as e:
        return Fail(message=f"获取排班信息失败: {str(e)}")


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
    try:
        result = await AppointmentService.get_doctor_appointments(db_session, doctor_id)
        return Success(result=result)
    except ValueError as e:
        return Fail(message=str(e), api_code=404)
    except Exception as e:
        return Fail(message=f"获取预约列表失败: {str(e)}")
