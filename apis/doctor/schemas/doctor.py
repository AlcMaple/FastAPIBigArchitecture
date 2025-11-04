from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============ 请求 Schema ============

class DoctorCreateRequest(BaseModel):
    """创建医生请求模型"""

    name: str = Field(..., min_length=1, max_length=50, description="医生姓名")
    department: str = Field(..., max_length=50, description="科室")
    title: str = Field(..., max_length=50, description="职称")
    specialty: str = Field(..., max_length=200, description="专长")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    years_experience: Optional[int] = Field(None, ge=0, description="从业年限")
    introduction: Optional[str] = Field(None, description="医生简介")


class DoctorUpdateRequest(BaseModel):
    """更新医生请求模型"""

    name: Optional[str] = Field(None, min_length=1, max_length=50, description="医生姓名")
    department: Optional[str] = Field(None, max_length=50, description="科室")
    title: Optional[str] = Field(None, max_length=50, description="职称")
    specialty: Optional[str] = Field(None, max_length=200, description="专长")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    years_experience: Optional[int] = Field(None, ge=0, description="从业年限")
    introduction: Optional[str] = Field(None, description="医生简介")
    available: Optional[bool] = Field(None, description="是否可预约")


# ============ 响应 Schema ============

class DoctorDetailResponse(BaseModel):
    """医生详情响应模型 - 用于获取、创建、更新等操作"""

    id: int = Field(..., description="医生ID")
    name: str = Field(..., description="医生姓名")
    department: str = Field(..., description="科室")
    title: str = Field(..., description="职称")
    specialty: str = Field(..., description="专长")
    available: bool = Field(..., description="是否可预约")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    years_experience: Optional[int] = Field(None, description="从业年限")
    introduction: Optional[str] = Field(None, description="医生简介")
    avatar: Optional[str] = Field(None, description="医生头像路径")
    avatar_url: Optional[str] = Field(None, description="医生头像完整URL")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class DoctorListItemResponse(BaseModel):
    """医生列表项响应模型 - 简化字段"""

    id: int = Field(..., description="医生ID")
    name: str = Field(..., description="医生姓名")
    department: str = Field(..., description="科室")
    title: str = Field(..., description="职称")
    specialty: str = Field(..., description="专长")
    available: bool = Field(..., description="是否可预约")
    avatar_url: Optional[str] = Field(None, description="医生头像完整URL")

    model_config = ConfigDict(from_attributes=True)


class DoctorListResponse(BaseModel):
    """医生列表响应模型 - 分页"""

    items: List[DoctorListItemResponse] = Field(..., description="医生列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class DoctorAvatarResponse(BaseModel):
    """医生头像响应模型"""

    doctor_id: int = Field(..., description="医生ID")
    avatar: Optional[str] = Field(None, description="头像相对路径")
    avatar_url: Optional[str] = Field(None, description="头像完整URL")


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""

    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件相对路径")
    file_url: str = Field(..., description="文件访问URL")
    file_size: int = Field(..., description="文件大小（字节）")
