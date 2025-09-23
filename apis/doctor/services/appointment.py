from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..repository.doctor import DoctorRepository
from ..repository.appointment import AppointmentRepository
from ..schemas.appointment import AppointmentRequest, AppointmentUpdateRequest
from .schedule import ScheduleService
from utils.datetime import diff_days_for_now_time


class AppointmentService:
    """预约业务服务层"""

    @staticmethod
    async def create_appointment(
        db_session: AsyncSession, appointment_request: AppointmentRequest
    ) -> Dict[str, Any]:
        """
        创建预约

        :param db_session: 数据库会话对象
        :param appointment_request: 预约请求
        :return: 预约结果
        """
        # 1. 检查医生是否存在
        doctor_info = await DoctorRepository.get_doctor_by_id(
            db_session, appointment_request.doctor_id
        )
        if not doctor_info:
            raise ValueError("医生信息不存在")

        # 2. 检查医生是否可预约
        if not doctor_info.get("available"):
            raise ValueError("该医生暂不可预约")

        # 3. 检查预约日期是否在未来
        days_diff = diff_days_for_now_time(appointment_request.appointment_date)
        if days_diff < 0:
            raise ValueError("不能预约过去的日期")

        # 4. 检查排班可用性
        availability = await ScheduleService.check_schedule_availability(
            db_session,
            appointment_request.doctor_id,
            appointment_request.appointment_date,
        )

        if not availability["available"]:
            raise ValueError(availability["reason"])

        # 5. 业务逻辑验证
        if not appointment_request.patient_name.strip():
            raise ValueError("患者姓名不能为空")

        if not appointment_request.phone.strip():
            raise ValueError("联系电话不能为空")

        # 6. 创建预约记录
        appointment_data = {
            "doctor_id": appointment_request.doctor_id,
            "patient_name": appointment_request.patient_name,
            "phone": appointment_request.phone,
            "appointment_date": appointment_request.appointment_date,
            "symptoms": appointment_request.symptoms,
        }

        appointment_result = await AppointmentRepository.create_appointment(
            db_session, appointment_data
        )

        # 7. 组装返回结果
        return {
            "appointment_id": appointment_result["appointment_id"],
            "doctor_name": doctor_info["name"],
            "patient_name": appointment_request.patient_name,
            "appointment_date": appointment_request.appointment_date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "status": "confirmed",
            "department": doctor_info["department"],
        }

    @staticmethod
    async def get_doctor_appointments(
        db_session: AsyncSession, doctor_id: int
    ) -> Dict[str, Any]:
        """
        获取医生的预约列表

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: 预约列表
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            raise ValueError("医生信息不存在")

        appointments = await AppointmentRepository.get_appointments_by_doctor(
            db_session, doctor_id
        )

        return {
            "doctor_name": doctor["name"],
            "appointments": appointments,
            "total": len(appointments),
        }

    @staticmethod
    async def get_appointment_detail(
        db_session: AsyncSession, appointment_id: int
    ) -> Dict[str, Any]:
        """
        获取预约详情

        :param db_session: 数据库会话对象
        :param appointment_id: 预约ID
        :return: 预约详情
        """
        appointment = await AppointmentRepository.get_appointment_by_id(
            db_session, appointment_id
        )

        if not appointment:
            raise ValueError("预约信息不存在")

        # 获取医生信息
        doctor = await DoctorRepository.get_doctor_by_id(
            db_session, appointment["doctor_id"]
        )
        if doctor:
            appointment["doctor_name"] = doctor["name"]
            appointment["department"] = doctor["department"]

        return appointment

    @staticmethod
    async def update_appointment(
        db_session: AsyncSession,
        appointment_id: int,
        appointment_request: AppointmentUpdateRequest,
    ) -> Dict[str, Any]:
        """
        更新预约信息

        :param db_session: 数据库会话对象
        :param appointment_id: 预约ID
        :param appointment_request: 更新预约请求
        :return: 更新后的预约信息
        """
        # 检查预约是否存在
        appointment = await AppointmentRepository.get_appointment_by_id(
            db_session, appointment_id
        )
        if not appointment:
            raise ValueError("预约信息不存在")

        # 过滤掉None值
        update_data = {
            k: v for k, v in appointment_request.dict().items() if v is not None
        }

        if not update_data:
            raise ValueError("没有需要更新的数据")

        # 如果更新预约日期，需要验证
        if "appointment_date" in update_data:
            days_diff = diff_days_for_now_time(update_data["appointment_date"])
            if days_diff < 0:
                raise ValueError("不能预约过去的日期")

            # 检查新日期的排班可用性
            availability = await ScheduleService.check_schedule_availability(
                db_session, appointment["doctor_id"], update_data["appointment_date"]
            )

            if not availability["available"]:
                raise ValueError(availability["reason"])

        # 调用Repository层更新预约
        updated_appointment = await AppointmentRepository.update_appointment(
            db_session, appointment_id, update_data
        )

        if not updated_appointment:
            raise ValueError("更新预约信息失败")

        return updated_appointment

    @staticmethod
    async def cancel_appointment(db_session: AsyncSession, appointment_id: int) -> bool:
        """
        取消预约

        :param db_session: 数据库会话对象
        :param appointment_id: 预约ID
        :return: 是否取消成功
        """
        # 检查预约是否存在
        appointment = await AppointmentRepository.get_appointment_by_id(
            db_session, appointment_id
        )
        if not appointment:
            raise ValueError("预约信息不存在")

        # 检查预约状态
        if appointment["status"] == "cancelled":
            raise ValueError("预约已经取消")

        if appointment["status"] == "completed":
            raise ValueError("已完成的预约不能取消")

        # 更新预约状态为取消
        update_data = {"status": "cancelled"}
        updated_appointment = await AppointmentRepository.update_appointment(
            db_session, appointment_id, update_data
        )

        return updated_appointment is not None

    @staticmethod
    async def get_patient_appointments(
        db_session: AsyncSession, patient_phone: str
    ) -> Dict[str, Any]:
        """
        根据患者电话获取预约列表

        :param db_session: 数据库会话对象
        :param patient_phone: 患者电话
        :return: 预约列表
        """
        if not patient_phone.strip():
            raise ValueError("患者电话不能为空")

        appointments = await AppointmentRepository.get_appointments_by_patient(
            db_session, patient_phone
        )

        # 为每个预约添加医生信息
        for appointment in appointments:
            doctor = await DoctorRepository.get_doctor_by_id(
                db_session, appointment["doctor_id"]
            )
            if doctor:
                appointment["doctor_name"] = doctor["name"]
                appointment["department"] = doctor["department"]

        return {
            "patient_phone": patient_phone,
            "appointments": appointments,
            "total": len(appointments),
        }
