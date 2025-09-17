from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any


class DoctorRepository:
    """医生数据访问层"""

    @staticmethod
    async def get_all_doctors(db_session: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取所有医生信息

        :param db_session: 数据库会话对象
        :return: 医生列表
        """
        # 模拟数据，实际项目中这里会查询数据库
        # 例如: result = await db_session.execute(select(Doctor))
        doctors_data = [
            {
                "id": 1,
                "name": "张医生",
                "department": "内科",
                "title": "主任医师",
                "specialty": "心血管疾病",
                "available": True,
            },
            {
                "id": 2,
                "name": "李医生",
                "department": "外科",
                "title": "副主任医师",
                "specialty": "骨科手术",
                "available": True,
            },
            {
                "id": 3,
                "name": "王医生",
                "department": "儿科",
                "title": "主治医师",
                "specialty": "儿童常见病",
                "available": False,
            },
            {
                "id": 4,
                "name": "陈医生",
                "department": "妇产科",
                "title": "副主任医师",
                "specialty": "妇科内分泌",
                "available": True,
            },
        ]
        return doctors_data

    @staticmethod
    async def get_doctor_by_id(
        db_session: AsyncSession, doctor_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        根据ID获取医生信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: 医生信息
        """
        # 实际项目中的查询示例：
        # result = await db_session.execute(
        #     select(Doctor).where(Doctor.id == doctor_id)
        # )
        # doctor = result.scalar_one_or_none()

        doctors_data = {
            1: {
                "id": 1,
                "name": "张医生",
                "department": "内科",
                "title": "主任医师",
                "specialty": "心血管疾病",
                "available": True,
            },
            2: {
                "id": 2,
                "name": "李医生",
                "department": "外科",
                "title": "副主任医师",
                "specialty": "骨科手术",
                "available": True,
            },
            3: {
                "id": 3,
                "name": "王医生",
                "department": "儿科",
                "title": "主治医师",
                "specialty": "儿童常见病",
                "available": False,
            },
            4: {
                "id": 4,
                "name": "陈医生",
                "department": "妇产科",
                "title": "副主任医师",
                "specialty": "妇科内分泌",
                "available": True,
            },
        }

        return doctors_data.get(doctor_id)

    @staticmethod
    async def get_available_doctors(db_session: AsyncSession) -> List[Dict[str, Any]]:
        """
        获取可预约的医生列表

        :param db_session: 数据库会话对象
        :return: 可预约医生列表
        """
        all_doctors = await DoctorRepository.get_all_doctors(db_session)
        return [doctor for doctor in all_doctors if doctor["available"]]

    @staticmethod
    async def get_doctors_by_department(
        db_session: AsyncSession, department: str
    ) -> List[Dict[str, Any]]:
        """
        根据科室获取医生列表

        :param db_session: 数据库会话对象
        :param department: 科室名称
        :return: 该科室的医生列表
        """
        all_doctors = await DoctorRepository.get_all_doctors(db_session)
        return [doctor for doctor in all_doctors if doctor["department"] == department]

    @staticmethod
    async def create_doctor(
        db_session: AsyncSession, doctor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建医生记录

        :param db_session: 数据库会话对象
        :param doctor_data: 医生数据
        :return: 创建的医生信息
        """
        # 实际项目中的创建示例：
        # new_doctor = Doctor(**doctor_data)
        # db_session.add(new_doctor)
        # await db_session.flush()

        # 模拟创建医生
        new_id = 100 + hash(str(doctor_data)) % 900
        doctor_data["id"] = new_id
        doctor_data["available"] = True

        return doctor_data

    @staticmethod
    async def update_doctor(
        db_session: AsyncSession, doctor_id: int, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新医生信息

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :param update_data: 更新数据
        :return: 更新后的医生信息
        """
        # 实际项目中的更新示例：
        # result = await db_session.execute(
        #     select(Doctor).where(Doctor.id == doctor_id)
        # )
        # doctor = result.scalar_one_or_none()
        # if doctor:
        #     for key, value in update_data.items():
        #         setattr(doctor, key, value)
        #     await db_session.refresh(doctor)

        # 模拟更新
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        if doctor:
            doctor.update(update_data)
            return doctor
        raise ValueError("Doctor not found")

    @staticmethod
    async def delete_doctor(db_session: AsyncSession, doctor_id: int) -> bool:
        """
        删除医生记录

        :param db_session: 数据库会话对象
        :param doctor_id: 医生ID
        :return: 是否删除成功
        """
        # 实际项目中的删除示例：
        # result = await db_session.execute(
        #     select(Doctor).where(Doctor.id == doctor_id)
        # )
        # doctor = result.scalar_one_or_none()
        # if doctor:
        #     await db_session.delete(doctor)
        #     return True

        # 模拟删除
        doctor = await DoctorRepository.get_doctor_by_id(db_session, doctor_id)
        return doctor is not None
