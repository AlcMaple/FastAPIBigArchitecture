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

    @staticmethod
    async def get_unit_by_id(
        db_session: AsyncSession, unit_id: int
    ) -> Optional[DesignUnit]:
        result = await db_session.execute(
            select(DesignUnit).where(DesignUnit.id == unit_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_units(
        db_session: AsyncSession, size: int, page: int
    ) -> List[DesignUnit]:
        """
        size:一页显示多少数据
        page:第几页
        """
        result = await db_session.execute(
            select(DesignUnit).limit(size).offset(size * (page - 1))
        )
        return result.scalars().all()

    @staticmethod
    async def update_unit(
        db_session: AsyncSession, unit_id: int, unit_data: Dict[str, Any]
    ) -> Optional[DesignUnit]:
        unit = await SimpleRepository.get_unit_by_id(db_session, unit_id)
        if unit is None:
            return None
        for key, value in unit_data.items():
            if hasattr(unit, key):
                setattr(unit, key, value)
        await db_session.flush()
        await db_session.refresh(unit)
        return unit

    @staticmethod
    async def delete_unit(db_session: AsyncSession, unit_id: int) -> bool:
        unit = await SimpleRepository.get_unit_by_id(db_session, unit_id)
        if unit is None:
            return False
        await db_session.delete(unit)
        await db_session.flush()
        return True
