"""
特点
    - 请求参数少、响应结果少
    - 接口没有复杂的业务逻辑，标题即内容的接口
"""

from fastapi import Depends, Query, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from exts.responses.api_response import Success
from . import router_simple
from ..schemas.simple import DesignUnitCreateRequest, DesignUnitUpdateRequest
from ..services.simple import SimpleService


@router_simple.post("/design_unit", summary="创建设计单位")
async def create_design_unit(
    request: DesignUnitCreateRequest,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    result = await SimpleService.create_unit(db_session, request)
    return Success(result, message="创建设计单位成功")


@router_simple.get("/design_unit/{unit_id}", summary="获取设计单位详情")
async def get_design_unit(
    unit_id: int = Path(..., description="Unique identifier of the design unit"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    result = await SimpleService.get_unit_by_id(db_session, unit_id)
    return Success(result, message="获取设计单位详情成功")


@router_simple.get("/design_units", summary="获取设计单位列表")
async def get_design_units(
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Page size"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    result = await SimpleService.get_units(db_session, page=page, size=page_size)
    return Success(result, message="获取设计单位列表成功")


@router_simple.put("/design_unit/{unit_id}", summary="更新设计单位")
async def update_design_unit(
    request: DesignUnitUpdateRequest,
    unit_id: int = Path(..., description="Unique identifier of the design unit"),
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    result = await SimpleService.update_unit(db_session, unit_id, request)
    return Success(result, message="更新设计单位成功")


@router_simple.delete("/design_unit/{unit_id}", summary="删除设计单位")
async def delete_design_unit(
    unit_id: int = Path(..., description="Unique identifier of the design unit"),
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    await SimpleService.delete_unit(db_session, unit_id)
    return Success(message="删除设计单位成功")
