from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "FastAPIBigArchitecture"
    debug: bool = True

    # JSON存储配置
    data_dir: str = "data"
    enable_backup: bool = True
    backup_retention_days: int = 7
    enable_file_lock: bool = True

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()
