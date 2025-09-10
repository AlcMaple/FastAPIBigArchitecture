#!/usr/bin/env python3
"""
创建测试数据库表的脚本
用于在pytest测试前创建bridge_db_test数据库的所有表
"""

import asyncio
import sys
from pathlib import Path

# 确保项目运行在根目录
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from config.settings import settings
from db.models import *


async def create_test_tables():
    """创建测试数据库所有表"""
    # 创建测试数据库引擎
    engine = create_async_engine(settings.test_database_url, echo=False)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        return True

    except Exception as e:
        return False
    finally:
        await engine.dispose()


def create_tables_sync():
    return asyncio.run(create_test_tables())


if __name__ == "__main__":
    result = create_tables_sync()
    if not result:
        sys.exit(1)
