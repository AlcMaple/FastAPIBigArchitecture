from typing import List, Optional, Dict, Any
from db.json_database import get_json_db


class DoctorRepository:
    """医生数据访问层"""

    @staticmethod
    async def get_all_doctors() -> List[Dict[str, Any]]:
        """
        获取所有医生信息

        :return: 医生列表
        """
        json_db = await get_json_db()
        return await json_db.find_all("doctors")

    @staticmethod
    async def get_doctor_by_id(doctor_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取医生信息

        :param doctor_id: 医生ID
        :return: 医生信息
        """
        json_db = await get_json_db()
        return await json_db.find_by_id("doctors", doctor_id)



    @staticmethod
    async def create_doctor(doctor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建医生记录

        :param doctor_data: 医生数据
        :return: 创建的医生信息
        """
        json_db = await get_json_db()
        if "available" not in doctor_data:
            doctor_data["available"] = True
        return await json_db.create("doctors", doctor_data)

    @staticmethod
    async def update_doctor(
        doctor_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新医生信息

        :param doctor_id: 医生ID
        :param update_data: 更新数据
        :return: 更新后的医生信息
        """
        json_db = await get_json_db()
        return await json_db.update("doctors", doctor_id, update_data)

    @staticmethod
    async def delete_doctor(doctor_id: int) -> bool:
        """
        删除医生记录

        :param doctor_id: 医生ID
        :return: 是否删除成功
        """
        json_db = await get_json_db()
        return await json_db.delete("doctors", doctor_id)
