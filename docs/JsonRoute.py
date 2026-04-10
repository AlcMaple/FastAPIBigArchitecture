import json
import time
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse

class JsonRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # 1. 获取原生响应
            response: Response = await original_route_handler(request)

            # 2. 只拦截 application/json 且状态码为 2xx 的正常响应
            if response.media_type == "application/json" and 200 <= response.status_code < 300:
                try:
                    body_content = response.body.decode("utf-8")
                    data = json.loads(body_content) if body_content else None
                except Exception:
                    data = None
                
                # 3. 重新组装外壳
                wrapped_content = {
                    "success": True,
                    "code": response.status_code,
                    "message": "操作成功",
                    "data": data,
                    "timestamp": int(time.time() * 1000)
                }
                
                # 4. 重点：必须继承原有的 headers 和 background 任务！
                return JSONResponse(
                    content=wrapped_content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    background=response.background
                )
            
            # 非 JSON 响应（如文件流、HTML等），直接放行，不做任何包装
            return response

        return custom_route_handler