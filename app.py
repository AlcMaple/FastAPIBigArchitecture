from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import os

# 导入中间件
from middlewares.logger.middleware import LogerMiddleware

# 导入配置
from config.settings import settings

# 日志配置
from exts.logururoute.config import setup_loggers

setup_loggers("./")

from db.init_db import init_database
from db.database import async_engine
from exts.logururoute.business_logger import logger
from exts.exceptions.handlers import ApiExceptionHandler

# 导入路由分组
from apis import router_doctor, router_appointment


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


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    description=" FastAPI 管理系统API",
    version="1.0.0",
    lifespan=lifespan,
)

# 初始化异常处理器
exception_handler = ApiExceptionHandler()
exception_handler.init_app(app)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # 添加日志中间件
# app.add_middleware(
#     LogerMiddleware,
#     is_record_useragent=True,  # 记录用户代理信息
#     is_record_headers=False,  # 不记录请求头信息
#     nesss_access_heads_keys=[],  # 不记录特定请求头
#     ignore_url=[
#         "/favicon.ico",
#         "/health",
#         "/docs",
#         "/redoc",
#         "/openapi.json",
#         "/static",
#     ],  # 忽略的URL
# )

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由分组
app.include_router(router_doctor)
app.include_router(router_appointment)
