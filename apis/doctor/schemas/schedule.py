from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class SchedulingInfo(BaseModel):
    """排班信息模型"""

    id: int
    doctor_id: int
    date: datetime = Field(..., description="排班日期")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    max_patients: int = Field(10, description="最大接诊数")
    current_patients: int = Field(0, description="当前预约数")

    model_config = ConfigDict(from_attributes=True)


class ScheduleCreateRequest(BaseModel):
    """创建排班请求模型"""

    doctor_id: int = Field(..., description="医生ID")
    date: datetime = Field(..., description="排班日期")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    max_patients: int = Field(10, description="最大接诊数")


class ScheduleUpdateRequest(BaseModel):
    """更新排班请求模型"""

    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    max_patients: Optional[int] = Field(None, description="最大接诊数")


class ScheduleListResponse(BaseModel):
    """排班列表响应模型"""

    schedules: List[SchedulingInfo]
    total: int
