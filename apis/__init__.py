from fastapi import APIRouter

from .base.api import router_simple, router_user

router_simple_module = APIRouter()
router_simple_module.include_router(router_simple)
router_simple_module.include_router(router_user)

__all__ = ["router_simple_module"]
