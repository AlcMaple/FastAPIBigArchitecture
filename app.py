from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 导入配置
from config.settings import settings

# 日志配置
from exts.logururoute.config import setup_loggers

setup_loggers("./")

from db.init_db import init_database
from db.database import async_engine
from exts.logururoute.business_logger import logger

# 导入应用工厂
from app_factory import get_app_factory

# 导入模块路由
from apis import router_doctor_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""

    # 启动时的初始化代码
    logger.info("启动 fastapi arch")

    # 初始化数据库表
    try:
        await init_database()
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")

    yield

    # 关闭时的清理代码
    logger.info("关闭 fastapi arch")
    # 关闭数据库连接池
    await async_engine.dispose()
    logger.info("关闭数据库连接")


def setup_applications():
    """设置应用配置"""
    factory = get_app_factory()

    # 注册模块
    # 每个模块会生成独立的子应用，可通过 /{module_name}/docs 访问
    # doctor 模块包含：医生信息路由分组 + 预约管理路由分组
    factory.register_module("doctor", router_doctor_module, "医疗服务模块")

    # 如果有其他模块（如 hospital），也在这里注册：
    # factory.register_module("hospital", router_hospital_module, "医院管理模块")

    # 创建所有应用（主应用 + 各模块子应用）
    main_app, module_apps = factory.create_all_apps(lifespan)

    # 配置静态文件服务（仅主应用需要）
    main_app.mount("/static", StaticFiles(directory="static"), name="static")

    # 挂载模块子应用到主应用
    # 访问方式：
    # - 主应用文档（所有API）：http://localhost:8000/docs
    # - doctor 子应用文档（医生+预约）：http://localhost:8000/doctor/docs
    #   在 doctor 子应用中，API 按 tags 分组显示：
    #     * 医生信息模块 (router_doctor)
    #     * 预约管理模块 (router_appointment)
    factory.mount_module_apps(main_app, module_apps)

    return main_app


# 创建应用实例
app = setup_applications()

# # 添加日志中间件
# from middlewares.logger.middleware import LogerMiddleware
# app.add_middleware(
#     LogerMiddleware,
#     is_record_useragent=True,
#     is_record_headers=False,
#     nesss_access_heads_keys=[],
#     ignore_url=[
#         "/favicon.ico",
#         "/health",
#         "/docs",
#         "/redoc",
#         "/openapi.json",
#         "/static",
#     ],
# )
