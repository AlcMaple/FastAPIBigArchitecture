import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from db.init_db import init_database
from db.database import async_engine
from exts.logururoute.business_logger import logger
from exts.exceptions.exception_handler import GlobalExceptionHandler

from routers.example import router as example_router
from routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动 fastapi arch")

    try:
        await init_database()
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")

    yield

    logger.info("关闭 fastapi arch")
    await async_engine.dispose()
    logger.info("关闭数据库连接")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.app_name,
        description="专为 AI 辅助编程、零配置的 FastAPI 脚手架",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 全局异常处理
    GlobalExceptionHandler().init_app(app)

    # 注册路由
    app.include_router(example_router)
    app.include_router(user_router)

    # 静态文件
    static_dir = "static"
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


app = create_app()
