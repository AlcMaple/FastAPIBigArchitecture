"""
测试数据库管理器
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config.settings import settings


class TestDatabaseManager:
    """测试数据库管理器"""

    def __init__(self):
        self.db_type = settings.test_db_type
        self.database_url = settings.effective_test_database_url
        self.engine = None
        self.session_factory = None

    def create_engine(self):
        """根据数据库类型创建引擎"""
        if self.db_type == "sqlite":
            # SQLite 配置
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                # SQLite 内存数据库配置
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                },
            )
        else:
            # MySQL 配置
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=1,
                max_overflow=0,
            )

        # 创建会话工厂
        self.session_factory = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

        return self.engine

    def get_session(self):
        """获取会话"""
        if self.session_factory is None:
            self.create_engine()
        return self.session_factory

    def get_engine(self):
        """获取数据库引擎"""
        if self.engine is None:
            self.create_engine()
        return self.engine

    async def dispose_engine(self):
        """关闭数据库引擎"""
        if self.engine:
            await self.engine.dispose()


# 测试数据库管理器实例
test_db_manager = TestDatabaseManager()
