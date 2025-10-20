#!/usr/bin/env python3
"""
创建测试数据库表的脚本
"""

import asyncio
import sys
from pathlib import Path

# 确保项目运行在根目录
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import SQLModel
from config.settings import settings
from db.models import *
from testcase.manager import manager


async def create_test_tables():
    """创建测试数据库表"""

    try:
        # 获取测试数据库引擎
        engine = manager.get_engine()

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        return True

    except Exception as e:
        return False
    finally:
        # MySQL 测试数据库需要关闭数据库引擎
        if settings.test_db_type != "sqlite":
            await manager.dispose_engine()


def create_tables_sync():
    return asyncio.run(create_test_tables())


if __name__ == "__main__":
    result = create_tables_sync()
    if not result:
        sys.exit(1)
