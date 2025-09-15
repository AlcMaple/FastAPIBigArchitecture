from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


class ScheduleRepository:
    """排班数据访问层"""

    @staticmethod
    async def get_doctor_schedules(
        db_session: AsyncSession, doctor_id: int, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        获取医生排班信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param days: 获取未来几天的排班，默认7天
        :return: 排班信息列表
        """
        # 实际项目中的查询示例：
        # result = await db_session.execute(
        #     select(Schedule).where(
        #         and_(
        #             Schedule.doctor_id == doctor_id,
        #             Schedule.date >= datetime.now().date(),
        #             Schedule.date <= datetime.now().date() + timedelta(days=days)
        #         )
        #     )
        # )

        # 模拟未来N天的排班数据
        schedules = []
        base_date = datetime.now().date()

        for i in range(days):
            schedule_date = base_date + timedelta(days=i)
            schedules.append(
                {
                    "id": i + 1,
                    "doctor_id": doctor_id,
                    "date": datetime.combine(schedule_date, datetime.min.time()),
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "max_patients": 10,
                    "current_patients": i + 2 if i < 5 else 0,
                    "available_slots": max(0, 10 - (i + 2 if i < 5 else 0)),
                }
            )

        return schedules

    @staticmethod
    async def get_schedule_by_date(
        db_session: AsyncSession, doctor_id: int, date: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定日期的医生排班信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param date: 日期
        :return: 排班信息
        """
        schedules = await ScheduleRepository.get_doctor_schedules(
            db_session, doctor_id, 30
        )
        target_date = date.date()

        for schedule in schedules:
            if schedule["date"].date() == target_date:
                return schedule

        return None

    @staticmethod
    async def create_schedule(
        db_session: AsyncSession, schedule_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建排班记录

        :param db_session: 数据库会话对象
        :param schedule_data: 排班数据
        :return: 创建的排班信息
        """
        # 实际项目中的创建示例：
        # new_schedule = Schedule(**schedule_data)
        # db_session.add(new_schedule)
        # await db_session.flush()

        # 模拟创建排班
        schedule_id = 1000 + hash(str(schedule_data)) % 9000
        schedule_data["id"] = schedule_id
        schedule_data["current_patients"] = 0
        schedule_data["available_slots"] = schedule_data.get("max_patients", 10)

        return schedule_data

    @staticmethod
    async def update_schedule(
        db_session: AsyncSession, schedule_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新排班信息

        :param db_session: 数据库会话对象
        :param schedule_id: 排班ID
        :param update_data: 更新数据
        :return: 更新后的排班信息
        """
        # 实际项目中的更新示例：
        # result = await db_session.execute(
        #     select(Schedule).where(Schedule.id == schedule_id)
        # )
        # schedule = result.scalar_one_or_none()
        # if schedule:
        #     for key, value in update_data.items():
        #         setattr(schedule, key, value)
        #     await db_session.refresh(schedule)

        # 模拟更新（这里需要根据实际需要实现）
        return None

    @staticmethod
    async def delete_schedule(db_session: AsyncSession, schedule_id: int) -> bool:
        """
        删除排班记录

        :param db_session: 数据库会话对象
        :param schedule_id: 排班ID
        :return: 是否删除成功
        """
        # 实际项目中的删除示例：
        # result = await db_session.execute(
        #     select(Schedule).where(Schedule.id == schedule_id)
        # )
        # schedule = result.scalar_one_or_none()
        # if schedule:
        #     await db_session.delete(schedule)
        #     return True

        # 模拟删除
        return True
