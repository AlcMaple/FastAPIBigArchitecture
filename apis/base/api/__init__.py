from fastapi import APIRouter

router_simple = APIRouter(prefix="/api", tags=["简单路由模块"])

from . import simple
