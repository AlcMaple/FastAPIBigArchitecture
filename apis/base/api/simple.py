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
from ..schemas.simple import DesignUnitCreateRequest
from ..services.simple import SimpleService


@router_simple.post("/design_unit", summary="创建设计单位")
async def create_design_unit(
    request: DesignUnitCreateRequest,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    result = await SimpleService.create_unit(db_session, request)
    return Success(result, message="创建设计单位成功")
