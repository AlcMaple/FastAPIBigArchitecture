from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AppointmentRequest(BaseModel):
    """预约请求模型"""

    doctor_id: int = Field(..., description="医生ID")
    patient_name: str = Field(..., description="患者姓名")
    phone: str = Field(..., description="联系电话")
    appointment_date: datetime = Field(..., description="预约日期")
    symptoms: Optional[str] = Field(None, description="症状描述")


class AppointmentResponse(BaseModel):
    """预约响应模型"""

    appointment_id: int
    doctor_name: str
    patient_name: str
    appointment_date: str
    status: str
    department: Optional[str] = None


class AppointmentInfo(BaseModel):
    """预约信息模型"""

    appointment_id: int
    doctor_id: int
    patient_name: str = Field(..., description="患者姓名")
    phone: str = Field(..., description="联系电话")
    appointment_date: datetime = Field(..., description="预约日期")
    symptoms: Optional[str] = Field(None, description="症状描述")
    status: str = Field(..., description="预约状态")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class AppointmentUpdateRequest(BaseModel):
    """更新预约请求模型"""

    appointment_date: Optional[datetime] = Field(None, description="预约日期")
    symptoms: Optional[str] = Field(None, description="症状描述")
    status: Optional[str] = Field(None, description="预约状态")


class AppointmentListResponse(BaseModel):
    """预约列表响应模型"""

    appointments: List[AppointmentInfo]
    total: int
