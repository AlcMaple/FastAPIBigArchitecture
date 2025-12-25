from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "FastAPIBigArchitecture"
    debug: bool = True
    base_url: str = "http://localhost:8000"  # 应用基础URL，用于生成完整的文件访问路径
    log_dir: str = os.path.join(os.path.dirname(__file__), "../logs")  # 日志目录

    # 数据库配置
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/arch_db"
    database_echo: bool = False
    test_database_url: str = "sqlite+aiosqlite:///:memory:"

    # mysql 连接池配置
    pool_size: int = 10
    max_overflow: int = 10
    pool_recycle: int = 3600
    pool_timeout: int = 30

    # JWT 配置
    secret_key: str = (
        "your-secret-key-change-in-production-please-use-a-strong-random-string"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 90

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()
