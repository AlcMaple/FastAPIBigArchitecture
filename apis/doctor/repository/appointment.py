from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


class AppointmentRepository:
    """预约数据访问层"""

    @staticmethod
    async def create_appointment(
        db_session: AsyncSession, appointment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建预约记录

        :param db_session: 数据库会话对象
        :param appointment_data: 预约数据
        :return: 创建的预约信息
        """
        # 实际项目中的创建示例：
        # new_appointment = Appointment(**appointment_data)
        # db_session.add(new_appointment)

        # 模拟创建预约
        appointment_id = 10000 + hash(str(appointment_data)) % 90000

        return {
            "appointment_id": appointment_id,
            "doctor_id": appointment_data["doctor_id"],
            "patient_name": appointment_data["patient_name"],
            "phone": appointment_data["phone"],
            "appointment_date": appointment_data["appointment_date"],
            "symptoms": appointment_data.get("symptoms"),
            "status": "confirmed",
            "created_at": datetime.now(),
        }

    @staticmethod
    async def get_appointments_by_doctor(
        db_session: AsyncSession, doctor_id: int
    ) -> List[Dict[str, Any]]:
        """
        获取医生的预约列表

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: 预约列表
        """
        # 实际项目中的查询示例：
        # result = await db_session.execute(
        #     select(Appointment).where(Appointment.doctor_id == doctor_id)
        # )
        # appointments = result.scalars().all()

        # 模拟数据
        appointments = [
            {
                "appointment_id": 10001,
                "doctor_id": doctor_id,
                "patient_name": "患者A",
                "phone": "138****1234",
                "appointment_date": datetime.now() + timedelta(days=1),
                "status": "confirmed",
                "symptoms": "头痛，发热",
                "created_at": datetime.now() - timedelta(hours=2),
            },
            {
                "appointment_id": 10002,
                "doctor_id": doctor_id,
                "patient_name": "患者B",
                "phone": "139****5678",
                "appointment_date": datetime.now() + timedelta(days=2),
                "status": "pending",
                "symptoms": "腹痛",
                "created_at": datetime.now() - timedelta(hours=1),
            },
        ]

        return appointments

    @staticmethod
    async def get_appointment_by_id(
        db_session: AsyncSession, appointment_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        根据ID获取预约信息

        :param db_session: 数据库会话对象
        :param appointment_id: 预约ID
        :return: 预约信息
        """
        # 实际项目中的查询示例：
        # result = await db_session.execute(
        #     select(Appointment).where(Appointment.id == appointment_id)
        # )
        # appointment = result.scalar_one_or_none()

        # 模拟查询
        appointments_data = {
            10001: {
                "appointment_id": 10001,
                "doctor_id": 1,
                "patient_name": "患者A",
                "phone": "138****1234",
                "appointment_date": datetime.now() + timedelta(days=1),
                "status": "confirmed",
                "symptoms": "头痛，发热",
                "created_at": datetime.now() - timedelta(hours=2),
            }
        }

        return appointments_data.get(appointment_id)

    @staticmethod
    async def update_appointment(
        db_session: AsyncSession, appointment_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新预约信息

        :param db_session: 数据库会话对象
        :param appointment_id: 预约ID
        :param update_data: 更新数据
        :return: 更新后的预约信息
        """
        # 实际项目中的更新示例：
        # result = await db_session.execute(
        #     select(Appointment).where(Appointment.id == appointment_id)
        # )
        # appointment = result.scalar_one_or_none()
        # if appointment:
        #     for key, value in update_data.items():
        #         setattr(appointment, key, value)

        # 模拟更新
        appointment = await AppointmentRepository.get_appointment_by_id(
            db_session, appointment_id
        )
        if appointment:
            appointment.update(update_data)
            return appointment
        return None

    @staticmethod
    async def delete_appointment(db_session: AsyncSession, appointment_id: int) -> bool:
        """
        删除预约记录

        :param db_session: 数据库会话对象
        :param appointment_id: 预约ID
        :return: 是否删除成功
        """
        # 实际项目中的删除示例：
        # result = await db_session.execute(
        #     select(Appointment).where(Appointment.id == appointment_id)
        # )
        # appointment = result.scalar_one_or_none()
        # if appointment:
        #     await db_session.delete(appointment)
        #     return True

        # 模拟删除
        appointment = await AppointmentRepository.get_appointment_by_id(
            db_session, appointment_id
        )
        return appointment is not None

    @staticmethod
    async def get_appointments_by_patient(
        db_session: AsyncSession, patient_phone: str
    ) -> List[Dict[str, Any]]:
        """
        根据患者电话获取预约列表

        :param db_session: 数据库会话对象
        :param patient_phone: 患者电话
        :return: 预约列表
        """
        # 实际项目中的查询示例：
        # result = await db_session.execute(
        #     select(Appointment).where(Appointment.phone == patient_phone)
        # )
        # appointments = result.scalars().all()

        # 模拟根据电话查询预约
        all_appointments = [
            {
                "appointment_id": 10001,
                "doctor_id": 1,
                "patient_name": "患者A",
                "phone": "138****1234",
                "appointment_date": datetime.now() + timedelta(days=1),
                "status": "confirmed",
            }
        ]

        return [apt for apt in all_appointments if apt["phone"] == patient_phone]
