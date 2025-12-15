from fastapi import APIRouter

# from .doctor.api import router_doctor

# # 创建 doctor 模块的完整路由（包含该模块下的所有路由分组）
# # 这个路由将作为 doctor 子应用使用，包含：
# # - router_doctor (医生信息路由分组，tag="医生信息模块")
# # - router_appointment (预约管理路由分组，tag="预约管理模块")
# router_doctor_module = APIRouter()
# router_doctor_module.include_router(router_doctor)

# # 如果有 hospital 模块，可以这样添加：
# # from .hospital.api import router_hospital_info, router_hospital_dept
# # router_hospital_module = APIRouter()
# # router_hospital_module.include_router(router_hospital_info)
# # router_hospital_module.include_router(router_hospital_dept)

# __all__ = [
#     "router_doctor_module",  # doctor 模块完整路由（包含医生+预约，用于子应用）
# ]

from .base.api import router_simple

router_simple_module = APIRouter()
router_simple_module.include_router(router_simple)

__all__ = ["router_simple_module"]
