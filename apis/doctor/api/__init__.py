from fastapi import APIRouter

# 创建医生模块的路由分组对象
router_doctor = APIRouter(prefix="/api/v1", tags=["医生信息模块"])

# 导入医生API模块
from . import doctor
