from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from fastapi import UploadFile

from ..repository.simple import SimpleRepository
from ..schemas.simple import DesignUnitCreateRequest, DesignUnitResponse
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
            raise ApiException(
                ErrorCode.RESOURCE_ALREADY_EXISTS, "该设计单元名称已存在"
            )
        unit_orm = await SimpleRepository.create_unit(
            db_session, unit_create_request.model_dump()
        )
        return DesignUnitResponse.model_validate(unit_orm)
