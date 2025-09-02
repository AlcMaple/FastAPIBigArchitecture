from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 导入路由分组
from apis import router_doctor

# 导入中间件
from middlewares.loger.middleware import LogerMiddleware

# 导入配置
from config.settings import settings

from db.init_db import init_database
from db.database import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化代码
    print("应用启动中...")

    # 初始化数据库表
    try:
        await init_database()
    except Exception as e:
        print(f"数据库初始化失败: {e}")

    yield

    # 关闭时的清理代码
    print("应用关闭中...")
    # 关闭数据库连接池
    await async_engine.dispose()
    print("数据库连接池已关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    description="基于FastAPI的医疗管理系统API",
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
    log_pro_path="./",  # 当前项目根目录
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


@app.get("/", summary="健康检查")
async def root():
    """根路径健康检查"""
    return {"message": "医疗管理系统API正在运行", "status": "healthy"}


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "服务运行正常"}
