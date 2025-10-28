from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "FastAPIBigArchitecture"
    debug: bool = True

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./arch_db.sqlite"
    database_echo: bool = False
    test_database_url: str = "sqlite+aiosqlite:///:memory:"

    # 测试数据导入脚本配置（按执行顺序）
    test_data_import_scripts: list[str] = [
        # "utils/import_bridge_base_data.py",
        # "utils/update_base_details.py",
    ]

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()
