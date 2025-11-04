from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class DoctorInfo(BaseModel):
    """医生信息模型"""

    id: int
    name: str = Field(..., description="医生姓名")
    department: str = Field(..., description="科室")
    title: str = Field(..., description="职称")
    specialty: str = Field(..., description="专长")
    available: bool = Field(True, description="是否可预约")

    model_config = ConfigDict(from_attributes=True)


class DoctorListResponse(BaseModel):
    """医生列表响应模型"""

    doctors: List[DoctorInfo]
    total: int


class DoctorDetailResponse(BaseModel):
    """医生详细信息响应模型"""

    id: int
    name: str = Field(..., description="医生姓名")
    department: str = Field(..., description="科室")
    title: str = Field(..., description="职称")
    specialty: str = Field(..., description="专长")
    available: bool = Field(True, description="是否可预约")

    model_config = ConfigDict(from_attributes=True)


class DoctorsByDepartmentResponse(BaseModel):
    """根据科室获取医生列表响应模型"""

    doctors: List[DoctorInfo]
    department: str
    total: int


class DoctorCreateResponse(BaseModel):
    """创建医生响应模型"""

    id: int
    name: str
    department: str
    title: str
    specialty: str
    available: bool = True

    model_config = ConfigDict(from_attributes=True)


class DoctorUpdateResponse(BaseModel):
    """更新医生响应模型"""

    id: int
    name: str
    department: str
    title: str
    specialty: str
    available: bool

    model_config = ConfigDict(from_attributes=True)


class DoctorDeleteResponse(BaseModel):
    """删除医生响应模型"""

    success: bool = Field(..., description="是否删除成功")
    doctor_id: int = Field(..., description="被删除的医生ID")


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""

    doctor_id: int
    file_path: str
    original_filename: Optional[str] = None
    content_type: Optional[str] = None


class AvatarUploadResponse(BaseModel):
    """头像上传响应模型"""

    doctor_id: int
    avatar: str
    original_filename: Optional[str] = None


class AvatarInfoResponse(BaseModel):
    """头像信息响应模型"""

    doctor_id: int
    doctor_name: str
    avatar: Optional[str] = None
    has_avatar: bool


class DoctorCreateRequest(BaseModel):
    """创建医生请求模型"""

    name: str = Field(..., description="医生姓名")
    department: str = Field(..., description="科室")
    title: str = Field(..., description="职称")
    specialty: str = Field(..., description="专长")


class DoctorUpdateRequest(BaseModel):
    """更新医生请求模型"""

    name: Optional[str] = Field(None, description="医生姓名")
    department: Optional[str] = Field(None, description="科室")
    title: Optional[str] = Field(None, description="职称")
    specialty: Optional[str] = Field(None, description="专长")
    available: Optional[bool] = Field(None, description="是否可预约")
