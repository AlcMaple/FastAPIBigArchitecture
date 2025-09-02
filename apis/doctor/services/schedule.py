from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..repository.doctor import DoctorRepository
from ..repository.schedule import ScheduleRepository
from ..schemas.schedule import ScheduleCreateRequest, ScheduleUpdateRequest


class ScheduleService:
    """排班业务服务层"""

    @staticmethod
    async def get_doctor_schedules(
        db_session: AsyncSession, doctor_id: int, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        获取医生排班信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param days: 获取未来几天的排班
        :return: 排班信息列表
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if not doctor:
            return []

        schedules = await ScheduleRepository.get_doctor_schedules(
            db_session, doctor_id, days
        )

        # 为每个排班添加医生信息
        for schedule in schedules:
            schedule["doctor_name"] = doctor["name"]
            schedule["department"] = doctor["department"]

        return schedules

    @staticmethod
    async def check_schedule_availability(
        db_session: AsyncSession, doctor_id: int, appointment_date: datetime
    ) -> Dict[str, Any]:
        """
        检查指定日期的排班可用性

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param appointment_date: 预约日期
        :return: 可用性信息
        """
        schedule = await ScheduleRepository.get_schedule_by_date(
            db_session, doctor_id, appointment_date
        )

        if not schedule:
            return {"available": False, "reason": "该日期无排班"}

        if schedule["current_patients"] >= schedule["max_patients"]:
            return {"available": False, "reason": "该日期预约已满"}

        return {
            "available": True,
            "available_slots": schedule["available_slots"],
            "max_patients": schedule["max_patients"],
            "current_patients": schedule["current_patients"],
        }

    @staticmethod
    async def create_schedule(
        db_session: AsyncSession, schedule_request: ScheduleCreateRequest
    ) -> Dict[str, Any]:
        """
        创建排班

        :param db_session: 数据库会话对象
        :param schedule_request: 创建排班请求
        :return: 创建的排班信息
        """
        # 检查医生是否存在
        doctor = await DoctorRepository.get_doctor_by_id(
            db_session, schedule_request.doctor_id
        )
        if not doctor:
            raise ValueError("医生信息不存在")

        # 业务逻辑验证
        if schedule_request.date.date() <= datetime.now().date():
            raise ValueError("排班日期必须是未来日期")

        if schedule_request.max_patients <= 0:
            raise ValueError("最大接诊数必须大于0")

        # 转换为字典
        schedule_data = schedule_request.dict()

        # 调用Repository层创建排班
        new_schedule = await ScheduleRepository.create_schedule(
            db_session, schedule_data
        )

        # 添加医生信息
        new_schedule["doctor_name"] = doctor["name"]
        new_schedule["department"] = doctor["department"]

        return new_schedule

    @staticmethod
    async def update_schedule(
        db_session: AsyncSession,
        schedule_id: int,
        schedule_request: ScheduleUpdateRequest,
    ) -> Dict[str, Any]:
        """
        更新排班信息

        :param db_session: 数据库会话对象
        :param schedule_id: 排班ID
        :param schedule_request: 更新排班请求
        :return: 更新后的排班信息
        """
        # 过滤掉None值
        update_data = {
            k: v for k, v in schedule_request.dict().items() if v is not None
        }

        if not update_data:
            raise ValueError("没有需要更新的数据")

        # 业务逻辑验证
        if "max_patients" in update_data and update_data["max_patients"] <= 0:
            raise ValueError("最大接诊数必须大于0")

        # 调用Repository层更新排班
        updated_schedule = await ScheduleRepository.update_schedule(
            db_session, schedule_id, update_data
        )

        if not updated_schedule:
            raise ValueError("排班信息不存在或更新失败")

        return updated_schedule

    @staticmethod
    async def delete_schedule(db_session: AsyncSession, schedule_id: int) -> bool:
        """
        删除排班

        :param db_session: 数据库会话对象
        :param schedule_id: 排班ID
        :return: 是否删除成功
        """
        # TODO: 这里可以添加业务逻辑检查
        # 例如：检查该排班是否有预约等

        # 调用Repository层删除排班
        success = await ScheduleRepository.delete_schedule(db_session, schedule_id)

        if not success:
            raise ValueError("删除排班失败")

        return success
