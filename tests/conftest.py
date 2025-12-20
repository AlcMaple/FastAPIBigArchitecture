"""
全局测试配置文件
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """
    配置全局 event loop
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
