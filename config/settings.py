from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "FastAPIBigArchitecture"
    debug: bool = True

    # 数据库配置
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/arch_db"
    database_echo: bool = False
    test_database_url: str = "sqlite+aiosqlite:///:memory:"

    # mysql 连接池配置
    pool_size: int = 10
    max_overflow: int = 10
    pool_recycle: int = 3600
    pool_timeout: int = 30

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()
