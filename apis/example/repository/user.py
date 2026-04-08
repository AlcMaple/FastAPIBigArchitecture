from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any

from db.models import User


class UserRepository:
    @staticmethod
    async def create_user(db_session: AsyncSession, user_data: Dict[str, Any]) -> User:
        """创建用户"""
        user = User(**user_data)
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user

    @staticmethod
    async def get_user_by_id(db_session: AsyncSession, user_id: int) -> Optional[User]:
        """根据用户ID获取用户"""
        result = await db_session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_name(db_session: AsyncSession, name: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db_session.execute(select(User).where(User.name == name))
        return result.scalars().first()

    @staticmethod
    async def check_user_exists(db_session: AsyncSession, name: str) -> bool:
        """检查用户名是否已存在"""
        result = await db_session.execute(select(User).where(User.name == name))
        return result.scalars().first() is not None
