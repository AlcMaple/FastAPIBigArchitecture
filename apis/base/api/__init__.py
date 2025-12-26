from fastapi import APIRouter

router_simple = APIRouter(prefix="/api", tags=["简单模块"])
router_user = APIRouter(prefix="/api", tags=["用户模块"])

from . import simple
from . import user
