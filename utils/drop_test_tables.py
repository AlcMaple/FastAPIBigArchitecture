#!/usr/bin/env python3
"""
删除测试数据库表的脚本
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


async def drop_test_tables():
    """删除测试数据库表"""

    try:
        # 获取测试数据库引擎
        engine = manager.get_engine()

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        return True

    except Exception as e:
        return False
    finally:
        await manager.dispose_engine()


def drop_tables_sync():
    return asyncio.run(drop_test_tables())


if __name__ == "__main__":
    result = drop_tables_sync()
    if not result:
        sys.exit(1)
