from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from fastapi import UploadFile


class DoctorInfo(BaseModel):
    """医生信息模型"""

    id: int
    name: str = Field(..., description="医生姓名")
    department: str = Field(..., description="科室")
    title: str = Field(..., description="职称")
    specialty: str = Field(..., description="专长")
    available: bool = Field(True, description="是否可预约")
    avatar: Optional[str] = Field(None, description="医生头像路径")
    hire_date: Optional[date] = Field(None, description="入职日期")
    work_days: Optional[int] = Field(None, description="工作天数")

    model_config = ConfigDict(from_attributes=True)


class DoctorListResponse(BaseModel):
    """医生列表响应模型"""

    doctors: List[DoctorInfo]
    total: int


class DoctorCreateRequest(BaseModel):
    """创建医生请求模型"""

    name: str = Field(..., description="医生姓名")
    department: str = Field(..., description="科室")
    title: str = Field(..., description="职称")
    specialty: str = Field(..., description="专长")
    hire_date: Optional[date] = Field(None, description="入职日期")


class DoctorUpdateRequest(BaseModel):
    """更新医生请求模型"""

    name: Optional[str] = Field(None, description="医生姓名")
    department: Optional[str] = Field(None, description="科室")
    title: Optional[str] = Field(None, description="职称")
    specialty: Optional[str] = Field(None, description="专长")
    available: Optional[bool] = Field(None, description="是否可预约")
    hire_date: Optional[date] = Field(None, description="入职日期")


class DoctorAvatarUploadResponse(BaseModel):
    """医生头像上传响应模型"""

    avatar_path: str = Field(..., description="头像文件路径")
    message: str = Field(..., description="上传结果消息")
