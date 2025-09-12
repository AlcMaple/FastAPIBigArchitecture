from pydantic_settings import BaseSettings
from pydantic import ConfigDict, computed_field
from functools import lru_cache
import os


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "FastAPIBigArchitecture"
    debug: bool = True

    # 数据库配置
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/arch_db"
    database_echo: bool = False
    test_database_url: str = (
        "mysql+aiomysql://root:password@localhost:3306/arch_db_test"
    )
    test_db_type: str = "sqlite"  # mysql | sqlite
    sqlite_test_database_url: str = "sqlite+aiosqlite:///:memory:"

    # mysql 连接池配置
    pool_size: int = 10
    max_overflow: int = 10
    pool_recycle: int = 3600
    pool_timeout: int = 30

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @computed_field
    @property
    def effective_test_database_url(self) -> str:
        """根据测试数据库类型返回有效的测试数据库URL"""
        if self.test_db_type == "sqlite":
            return self.sqlite_test_database_url
        return self.test_database_url


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()
