from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from fastapi import UploadFile

from ..repository.simple import SimpleRepository
from ..schemas.simple import (
    DesignUnitCreateRequest,
    DesignUnitResponse,
    DesignUnitUpdateRequest,
)
from exts.logururoute.business_logger import logger
from utils.file import FileUtils, FileCategory
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode
from config.settings import settings


class SimpleService:
    @staticmethod
    async def create_unit(
        db_session: AsyncSession, unit_create_request: DesignUnitCreateRequest
    ) -> DesignUnitResponse:
        if await SimpleRepository.check(db_session, unit_create_request.name):
            raise ApiException(ErrorCode.RESOURCE_ALREADY_EXISTS, "设计单元名称已存在")
        unit_orm = await SimpleRepository.create_unit(
            db_session, unit_create_request.model_dump()
        )
        return DesignUnitResponse.model_validate(unit_orm)

    @staticmethod
    async def get_unit_by_id(
        db_session: AsyncSession, unit_id: int
    ) -> DesignUnitResponse:
        unit_orm = await SimpleRepository.get_unit_by_id(db_session, unit_id)
        if not unit_orm:
            raise ApiException(ErrorCode.NOT_FOUND)
        return DesignUnitResponse.model_validate(unit_orm)

    @staticmethod
    async def get_units(
        db_session: AsyncSession, size: int, page: int
    ) -> List[DesignUnitResponse]:
        units_orm = await SimpleRepository.get_units(db_session, size, page)
        return [DesignUnitResponse.model_validate(unit_orm) for unit_orm in units_orm]

    @staticmethod
    async def update_unit(
        db_session: AsyncSession,
        unit_id: int,
        unit_update_request: DesignUnitUpdateRequest,
    ) -> DesignUnitResponse:
        unit_orm = await SimpleRepository.update_unit(
            db_session, unit_id, unit_update_request.model_dump()
        )
        if not unit_orm:
            raise ApiException(ErrorCode.NOT_FOUND)
        return DesignUnitResponse.model_validate(unit_orm)

    @staticmethod
    async def delete_unit(db_session: AsyncSession, unit_id: int) -> bool:
        result = await SimpleRepository.delete_unit(db_session, unit_id)
        if not result:
            raise ApiException(ErrorCode.NOT_FOUND)
        return True
