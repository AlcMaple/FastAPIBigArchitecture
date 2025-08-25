from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    """预约状态枚举"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Doctor(SQLModel, table=True):
    """医生表"""

    __tablename__ = "doctors"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, description="医生姓名")
    department: str = Field(max_length=50, description="科室")
    title: str = Field(max_length=50, description="职称")
    specialty: str = Field(max_length=200, description="专长")
    available: bool = Field(default=True, description="是否可预约")
    phone: Optional[str] = Field(default=None, max_length=20, description="联系电话")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    years_experience: Optional[int] = Field(default=None, description="从业年限")
    introduction: Optional[str] = Field(default=None, description="医生简介")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关系
    schedules: List["Schedule"] = Relationship(back_populates="doctor")
    appointments: List["Appointment"] = Relationship(back_populates="doctor")


class Schedule(SQLModel, table=True):
    """排班表"""

    __tablename__ = "schedules"

    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="doctors.id", description="医生ID")
    date: datetime = Field(description="排班日期")
    start_time: str = Field(max_length=10, description="开始时间")
    end_time: str = Field(max_length=10, description="结束时间")
    max_patients: int = Field(default=10, description="最大接诊数")
    current_patients: int = Field(default=0, description="当前预约数")
    is_available: bool = Field(default=True, description="是否可用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关系
    doctor: Doctor = Relationship(back_populates="schedules")
    appointments: List["Appointment"] = Relationship(back_populates="schedule")


class Patient(SQLModel, table=True):
    """患者表"""

    __tablename__ = "patients"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, description="患者姓名")
    phone: str = Field(max_length=20, unique=True, description="联系电话")
    gender: Optional[str] = Field(default=None, max_length=10, description="性别")
    age: Optional[int] = Field(default=None, description="年龄")
    id_card: Optional[str] = Field(default=None, max_length=20, description="身份证号")
    address: Optional[str] = Field(default=None, max_length=200, description="地址")
    emergency_contact: Optional[str] = Field(
        default=None, max_length=50, description="紧急联系人"
    )
    emergency_phone: Optional[str] = Field(
        default=None, max_length=20, description="紧急联系电话"
    )
    medical_history: Optional[str] = Field(default=None, description="病史")
    allergies: Optional[str] = Field(default=None, description="过敏史")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关系
    appointments: List["Appointment"] = Relationship(back_populates="patient")


class Appointment(SQLModel, table=True):
    """预约表"""

    __tablename__ = "appointments"

    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="doctors.id", description="医生ID")
    patient_id: int = Field(foreign_key="patients.id", description="患者ID")
    schedule_id: int = Field(foreign_key="schedules.id", description="排班ID")
    appointment_date: datetime = Field(description="预约日期时间")
    symptoms: Optional[str] = Field(default=None, description="症状描述")
    status: AppointmentStatus = Field(
        default=AppointmentStatus.PENDING, description="预约状态"
    )
    appointment_number: Optional[str] = Field(
        default=None, max_length=20, description="预约号"
    )
    notes: Optional[str] = Field(default=None, description="备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关系
    doctor: Doctor = Relationship(back_populates="appointments")
    patient: Patient = Relationship(back_populates="appointments")
    schedule: Schedule = Relationship(back_populates="appointments")


class Hospital(SQLModel, table=True):
    """医院表"""

    __tablename__ = "hospitals"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="医院名称")
    address: str = Field(max_length=200, description="医院地址")
    phone: str = Field(max_length=20, description="联系电话")
    website: Optional[str] = Field(default=None, max_length=100, description="官方网站")
    description: Optional[str] = Field(default=None, description="医院介绍")
    level: Optional[str] = Field(default=None, max_length=20, description="医院等级")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class Department(SQLModel, table=True):
    """科室表"""

    __tablename__ = "departments"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True, description="科室名称")
    description: Optional[str] = Field(default=None, description="科室介绍")
    location: Optional[str] = Field(
        default=None, max_length=100, description="科室位置"
    )
    phone: Optional[str] = Field(default=None, max_length=20, description="科室电话")
    head_doctor: Optional[str] = Field(
        default=None, max_length=50, description="科室主任"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class MedicalRecord(SQLModel, table=True):
    """病历表"""

    __tablename__ = "medical_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(foreign_key="appointments.id", description="预约ID")
    diagnosis: str = Field(description="诊断结果")
    treatment: Optional[str] = Field(default=None, description="治疗方案")
    prescription: Optional[str] = Field(default=None, description="处方")
    follow_up_date: Optional[datetime] = Field(default=None, description="复诊日期")
    notes: Optional[str] = Field(default=None, description="医生备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
