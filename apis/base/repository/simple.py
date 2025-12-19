from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from fastapi import UploadFile
from datetime import datetime

from utils.file import FileUtils, FileCategory
from db.models import DesignUnit


class SimpleRepository:
    @staticmethod
    async def create_unit(
        db_session: AsyncSession, unit_data: Dict[str, Any]
    ) -> DesignUnit:
        unit = DesignUnit(**unit_data)
        db_session.add(unit)
        await db_session.flush()
        await db_session.refresh(unit)
        return unit

    @staticmethod
    async def check(db_session: AsyncSession, name: str) -> bool:
        result = await db_session.execute(
            select(DesignUnit).where(DesignUnit.name == name)
        )
        return result.scalars().first() is not None
