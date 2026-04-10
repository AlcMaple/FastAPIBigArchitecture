from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from exts.route import JsonRoute
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from db.models import DesignUnit
from utils.type import NameStr, AddressStr, MobilePhoneStr, EmailStr

# ======================== Schemas ========================

class DesignUnitCreateRequest(BaseModel):
    name: NameStr = Field(..., description="设计单位名称")
    tel: Optional[MobilePhoneStr] = Field(None, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[AddressStr] = Field(None, description="地址")
    contact: Optional[NameStr] = Field(None, description="联系人")


class DesignUnitUpdateRequest(BaseModel):
    name: Optional[NameStr] = Field(None, description="设计单位名称")
    tel: Optional[MobilePhoneStr] = Field(None, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[AddressStr] = Field(None, description="地址")
    contact: Optional[NameStr] = Field(None, description="联系人")


class DesignUnitResponse(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="设计单位名称")
    tel: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    contact: Optional[str] = Field(None, description="联系人")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ======================== Router ========================

router = APIRouter(prefix="/api", tags=["设计单位"], route_class=JsonRoute)


@router.post("/design_unit", summary="创建设计单位")
async def create_design_unit(
    payload: DesignUnitCreateRequest,
    db: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    existing = await db.execute(select(DesignUnit).where(DesignUnit.name == payload.name))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="设计单位名称已存在")

    unit = DesignUnit(**payload.model_dump())
    db.add(unit)
    await db.flush()
    await db.refresh(unit)
    return DesignUnitResponse.model_validate(unit)


@router.get("/design_unit/{unit_id}", summary="获取设计单位详情")
async def get_design_unit(
    unit_id: int = Path(..., description="设计单位ID"),
    db: AsyncSession = Depends(depends_get_db_session),
):
    result = await db.execute(select(DesignUnit).where(DesignUnit.id == unit_id))
    unit = result.scalars().first()
    if not unit:
        raise HTTPException(status_code=404, detail="设计单位不存在")
    return DesignUnitResponse.model_validate(unit)


@router.get("/design_units", summary="获取设计单位列表")
async def get_design_units(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(depends_get_db_session),
):
    result = await db.execute(
        select(DesignUnit).limit(page_size).offset(page_size * (page - 1))
    )
    units = result.scalars().all()
    return [DesignUnitResponse.model_validate(u) for u in units]


@router.put("/design_unit/{unit_id}", summary="更新设计单位")
async def update_design_unit(
    payload: DesignUnitUpdateRequest,
    unit_id: int = Path(..., description="设计单位ID"),
    db: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    result = await db.execute(select(DesignUnit).where(DesignUnit.id == unit_id))
    unit = result.scalars().first()
    if not unit:
        raise HTTPException(status_code=404, detail="设计单位不存在")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(unit, key, value)

    await db.flush()
    await db.refresh(unit)
    return DesignUnitResponse.model_validate(unit)


@router.delete("/design_unit/{unit_id}", summary="删除设计单位")
async def delete_design_unit(
    unit_id: int = Path(..., description="设计单位ID"),
    db: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    result = await db.execute(select(DesignUnit).where(DesignUnit.id == unit_id))
    unit = result.scalars().first()
    if not unit:
        raise HTTPException(status_code=404, detail="设计单位不存在")

    await db.delete(unit)
    await db.flush()
    return {"message": "删除成功"}
