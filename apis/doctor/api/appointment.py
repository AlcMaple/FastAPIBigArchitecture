from fastapi import Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from ..services.appointment import AppointmentService
from ..services.schedule import ScheduleService
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from exts.responses.json_response import Success, Fail
from . import router_appointment
from ..schemas.appointment import AppointmentRequest


@router_appointment.post("/appointment", summary="预约挂号")
async def create_appointment(
    appointment: AppointmentRequest,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    创建预约

    :param appointment: 预约信息
    :param db_session: 数据库连接依赖注入对象
    :return: 预约结果
    """
    try:
        appointment_result = await AppointmentService.create_appointment(
            db_session, appointment
        )
        return Success(result=appointment_result, message="预约成功")
    except ValueError as e:
        return Fail(message=str(e))
    except Exception as e:
        return Fail(message=f"预约失败: {str(e)}")


@router_appointment.post("/appointment/check", summary="检查预约可用性")
async def check_appointment_availability(
    doctor_id: int,
    appointment_date: str,
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    检查预约可用性

    :param doctor_id: 医生ID
    :param appointment_date: 预约日期 (格式: YYYY-MM-DD)
    :param db_session: 数据库连接依赖注入对象
    :return: 可用性检查结果
    """
    try:
        appointment_datetime = datetime.strptime(appointment_date, "%Y-%m-%d")

        availability = await ScheduleService.check_schedule_availability(
            db_session, doctor_id, appointment_datetime
        )
        return Success(result=availability)
    except ValueError as e:
        return Fail(message=f"日期格式错误: {str(e)}")
    except Exception as e:
        return Fail(message=f"检查可用性失败: {str(e)}")


@router_appointment.get("/appointment/{appointment_id}", summary="获取预约详情")
async def get_appointment_detail(
    appointment_id: int = Path(..., description="预约ID"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    获取预约详情

    :param appointment_id: 预约ID
    :param db_session: 数据库连接依赖注入对象
    :return: 预约详情
    """
    try:
        appointment = await AppointmentService.get_appointment_detail(
            db_session, appointment_id
        )
        if not appointment:
            return Fail(message="预约信息不存在", api_code=404)

        return Success(result=appointment)
    except Exception as e:
        return Fail(message=f"获取预约详情失败: {str(e)}")


@router_appointment.delete("/appointment/{appointment_id}", summary="取消预约")
async def cancel_appointment(
    appointment_id: int = Path(..., description="预约ID"),
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """
    取消预约

    :param appointment_id: 预约ID
    :param db_session: 数据库连接依赖注入对象
    :return: 取消结果
    """
    try:
        success = await AppointmentService.cancel_appointment(
            db_session, appointment_id
        )
        return Success(result={"cancelled": success}, message="预约取消成功")
    except ValueError as e:
        return Fail(message=str(e), api_code=404 if "不存在" in str(e) else 400)
    except Exception as e:
        return Fail(message=f"取消预约失败: {str(e)}")


@router_appointment.get(
    "/appointments/patient/{patient_phone}", summary="根据患者电话获取预约列表"
)
async def get_patient_appointments(
    patient_phone: str = Path(..., description="患者电话"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    根据患者电话获取预约列表

    :param patient_phone: 患者电话
    :param db_session: 数据库连接依赖注入对象
    :return: 患者预约列表
    """
    try:
        result = await AppointmentService.get_patient_appointments(
            db_session, patient_phone
        )
        return Success(result=result)
    except ValueError as e:
        return Fail(message=str(e))
    except Exception as e:
        return Fail(message=f"获取患者预约列表失败: {str(e)}")
