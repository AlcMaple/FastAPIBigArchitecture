from sqlmodel import SQLModel
import asyncio

from .database import async_engine
from .models import *
from exts.logururoute.business_logger import logger


async def create_tables():
    """创建数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_tables():
    """删除数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def init_database():
    """初始化数据库"""
    await create_tables()
    logger.info("数据表配置完成")


if __name__ == "__main__":
    asyncio.run(init_database())
