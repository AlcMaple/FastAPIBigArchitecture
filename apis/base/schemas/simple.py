from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from utils.type import NameStr, AddressStr, MobilePhoneStr, EmailStr


class DesignUnitCreateRequest(BaseModel):
    name: NameStr = Field(..., description="Name of the design unit")
    tel: Optional[MobilePhoneStr] = Field(
        None, description="Telephone number of the design unit"
    )
    email: Optional[EmailStr] = Field(
        None, description="Email address of the design unit"
    )
    address: Optional[AddressStr] = Field(
        None, description="Address of the design unit"
    )
    contact: Optional[NameStr] = Field(
        None, description="Name of the contact person for the design unit"
    )


class DesignUnitUpdateRequest(BaseModel):
    name: Optional[NameStr] = Field(None, description="Name of the design unit")
    tel: Optional[MobilePhoneStr] = Field(
        None, description="Telephone number of the design unit"
    )
    email: Optional[EmailStr] = Field(
        None, description="Email address of the design unit"
    )
    address: Optional[AddressStr] = Field(
        None, description="Address of the design unit"
    )
    contact: Optional[NameStr] = Field(
        None, description="Name of the contact person for the design unit"
    )


class DesignUnitResponse(BaseModel):
    id: int = Field(..., description="Unique identifier of the design unit")
    name: NameStr = Field(..., description="Name of the design unit")
    tel: Optional[MobilePhoneStr] = Field(
        None, description="Telephone number of the design unit"
    )
    email: Optional[EmailStr] = Field(
        None, description="Email address of the design unit"
    )
    address: Optional[AddressStr] = Field(
        None, description="Address of the design unit"
    )
    contact: Optional[NameStr] = Field(
        None, description="Name of the contact person for the design unit"
    )
    created_at: Optional[datetime] = Field(
        None, description="Date and time when the design unit was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Date and time when the design unit was last updated"
    )

    model_config = ConfigDict(from_attributes=True)
