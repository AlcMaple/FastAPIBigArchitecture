"""
测试数据工厂

用于在集成测试中生成测试数据
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional


class DoctorFactory:
    """医生数据工厂"""

    @staticmethod
    def create_doctor_data(
        name: str = "测试医生",
        department: str = "内科",
        title: str = "主治医师",
        specialization: Optional[str] = "心血管疾病",
        phone: Optional[str] = "13800138000",
        email: Optional[str] = "doctor@example.com",
        **kwargs
    ) -> Dict[str, Any]:
        """创建医生数据"""
        data = {
            "name": name,
            "department": department,
            "title": title,
            "specialization": specialization,
            "phone": phone,
            "email": email,
        }
        # 允许覆盖任何字段
        data.update(kwargs)
        return data

    @staticmethod
    def create_multiple_doctors(count: int = 3) -> list[Dict[str, Any]]:
        """批量创建医生数据"""
        departments = ["内科", "外科", "儿科", "妇科", "骨科"]
        titles = ["主任医师", "副主任医师", "主治医师", "住院医师"]

        doctors = []
        for i in range(count):
            doctor = DoctorFactory.create_doctor_data(
                name=f"测试医生{i + 1}",
                department=departments[i % len(departments)],
                title=titles[i % len(titles)],
                phone=f"138{i:08d}",
                email=f"doctor{i + 1}@example.com",
            )
            doctors.append(doctor)

        return doctors


class ScheduleFactory:
    """排班数据工厂"""

    @staticmethod
    def create_schedule_data(
        doctor_id: int = 1,
        schedule_date: Optional[date] = None,
        period: str = "上午",
        max_appointments: int = 10,
        available_slots: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """创建排班数据"""
        if schedule_date is None:
            # 默认创建明天的排班
            schedule_date = date.today() + timedelta(days=1)

        data = {
            "doctor_id": doctor_id,
            "schedule_date": schedule_date.isoformat(),
            "period": period,
            "max_appointments": max_appointments,
            "available_slots": available_slots,
        }
        data.update(kwargs)
        return data

    @staticmethod
    def create_weekly_schedules(doctor_id: int = 1) -> list[Dict[str, Any]]:
        """创建一周的排班数据"""
        schedules = []
        periods = ["上午", "下午"]

        for day in range(7):
            schedule_date = date.today() + timedelta(days=day + 1)
            for period in periods:
                schedule = ScheduleFactory.create_schedule_data(
                    doctor_id=doctor_id,
                    schedule_date=schedule_date,
                    period=period,
                )
                schedules.append(schedule)

        return schedules


class PatientFactory:
    """患者数据工厂"""

    @staticmethod
    def create_patient_data(
        name: str = "测试患者",
        id_card: str = "110101199001011234",
        gender: str = "男",
        age: int = 30,
        phone: str = "13900139000",
        address: Optional[str] = "北京市朝阳区",
        **kwargs
    ) -> Dict[str, Any]:
        """创建患者数据"""
        data = {
            "name": name,
            "id_card": id_card,
            "gender": gender,
            "age": age,
            "phone": phone,
            "address": address,
        }
        data.update(kwargs)
        return data

    @staticmethod
    def create_multiple_patients(count: int = 3) -> list[Dict[str, Any]]:
        """批量创建患者数据"""
        patients = []
        for i in range(count):
            patient = PatientFactory.create_patient_data(
                name=f"测试患者{i + 1}",
                id_card=f"11010119900101{i:04d}",
                gender="男" if i % 2 == 0 else "女",
                age=20 + i * 10,
                phone=f"139{i:08d}",
            )
            patients.append(patient)

        return patients


class AppointmentFactory:
    """预约数据工厂"""

    @staticmethod
    def create_appointment_data(
        patient_id: int = 1,
        doctor_id: int = 1,
        schedule_id: int = 1,
        appointment_date: Optional[date] = None,
        period: str = "上午",
        status: str = "已预约",
        **kwargs
    ) -> Dict[str, Any]:
        """创建预约数据"""
        if appointment_date is None:
            appointment_date = date.today() + timedelta(days=1)

        data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "schedule_id": schedule_id,
            "appointment_date": appointment_date.isoformat(),
            "period": period,
            "status": status,
        }
        data.update(kwargs)
        return data


class TestDataBuilder:
    """复合测试数据构建器"""

    @staticmethod
    def build_doctor_with_schedules(doctor_data: Optional[Dict] = None) -> Dict[str, Any]:
        """构建医生及其排班数据"""
        if doctor_data is None:
            doctor_data = DoctorFactory.create_doctor_data()

        schedules = ScheduleFactory.create_weekly_schedules(doctor_id=1)

        return {
            "doctor": doctor_data,
            "schedules": schedules,
        }

    @staticmethod
    def build_complete_appointment_scenario() -> Dict[str, Any]:
        """构建完整的预约场景（医生、患者、排班、预约）"""
        doctor = DoctorFactory.create_doctor_data()
        patient = PatientFactory.create_patient_data()
        schedule = ScheduleFactory.create_schedule_data()
        appointment = AppointmentFactory.create_appointment_data()

        return {
            "doctor": doctor,
            "patient": patient,
            "schedule": schedule,
            "appointment": appointment,
        }
