from typing import Dict, Tuple
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from exts.exceptions.handlers import ApiExceptionHandler


class AppFactory:
    """应用工厂类"""

    def __init__(self):
        self.modules = {}

    def register_module(self, name: str, router, description: str):
        """
        注册模块

        :param name: 模块名称（用于URL路径，如 'doctor'）
        :param router: FastAPI Router 实例
        :param description: 模块描述（用于文档）
        """
        self.modules[name] = {"router": router, "description": description}

    def create_module_app(self, module_name: str) -> FastAPI:
        """
        创建单个模块的子应用

        :param module_name: 模块名称
        :return: 模块的 FastAPI 应用实例
        """
        if module_name not in self.modules:
            raise ValueError(f"模块 '{module_name}' 未注册")

        module = self.modules[module_name]

        app = FastAPI(
            title=f"{settings.app_name} - {module['description']}",
            description=f"{module['description']}相关 API",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # 配置异常处理
        self._setup_exception_handling(app)

        # 包含模块路由
        app.include_router(module["router"])

        return app

    def create_main_app(self, lifespan) -> FastAPI:
        """
        创建主应用（包含所有模块）

        :param lifespan: 生命周期管理器
        :return: 主 FastAPI 应用实例
        """
        app = FastAPI(
            title=settings.app_name,
            description="FastAPI 管理系统API - 包含所有模块",
            version="1.0.0",
            lifespan=lifespan,
        )

        # 配置 CORS
        self._setup_cors(app)

        # 配置异常处理
        self._setup_exception_handling(app)

        # 包含所有模块路由
        for module in self.modules.values():
            app.include_router(module["router"])

        return app

    def create_all_apps(self, lifespan) -> Tuple[FastAPI, Dict[str, FastAPI]]:
        """
        创建主应用和所有模块子应用

        :param lifespan: 生命周期管理器（仅主应用使用）
        :return: (主应用, {模块名: 模块应用})
        """
        main_app = self.create_main_app(lifespan)
        module_apps = {}

        for module_name in self.modules.keys():
            module_apps[module_name] = self.create_module_app(module_name)

        return main_app, module_apps

    def mount_module_apps(self, main_app: FastAPI, module_apps: Dict[str, FastAPI]):
        """
        将模块子应用挂载到主应用

        访问方式：
        - 主应用文档：http://localhost:8000/docs
        - 模块文档：http://localhost:8000/{module_name}/docs
        - 主应用API：http://localhost:8000/api/v1/...
        - 模块API：http://localhost:8000/{module_name}/api/v1/...

        :param main_app: 主应用实例
        :param module_apps: 模块应用字典
        """
        for module_name, module_app in module_apps.items():
            main_app.mount(f"/{module_name}", module_app)

    def _setup_cors(self, app: FastAPI):
        """配置 CORS 中间件"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_exception_handling(self, app: FastAPI):
        """配置全局异常处理"""
        exception_handler = ApiExceptionHandler()
        exception_handler.init_app(app)


# 全局工厂实例
app_factory = AppFactory()


def get_app_factory() -> AppFactory:
    """获取应用工厂实例"""
    return app_factory
