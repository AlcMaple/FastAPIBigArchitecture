from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 导入路由分组
from apis import router_doctor

# 导入中间件
from middlewares.logger.middleware import LogerMiddleware

# 导入配置
from config.settings import settings
from exts.logururoute.config import setup_loggers
from exts.logururoute.business_logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 初始化中间件日志
    setup_loggers("./")

    # 启动时的初始化代码
    logger.info("启动 fastapi arch")

    yield

    # 关闭时的清理代码
    logger.info("关闭 fastapi arch")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    description=" FastAPI 管理系统API",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加日志中间件
app.add_middleware(
    LogerMiddleware,
    is_record_useragent=True,  # 记录用户代理信息
    is_record_headers=False,  # 不记录请求头信息
    nesss_access_heads_keys=[],  # 不记录特定请求头
    ignore_url=[
        "/favicon.ico",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ],  # 忽略的URL
)

# 注册路由分组
app.include_router(router_doctor)
