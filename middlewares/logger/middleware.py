from contextvars import ContextVar
from fastapi import Request
import shortuuid
from starlette.types import ASGIApp, Receive, Scope, Send
from user_agents import parse
from urllib.parse import parse_qs
from datetime import datetime
import typing
from time import perf_counter
from starlette.requests import Request as StarletteRequest

from exts.requestvar.bing import bind_contextvar
from exts.logururoute.config import async_trace_add_log_record

request_var: ContextVar[Request] = ContextVar("request")
request: Request = bind_contextvar(request_var)


class LogerMiddleware:
    def __init__(
        self,
        *,
        app: ASGIApp,
        is_record_useragent=False,
        is_record_headers=False,
        nesss_access_heads_keys=[],
        ignore_url: typing.List = ["/favicon.ico", "websocket"],
    ) -> None:
        self.app = app
        self.is_record_useragent = is_record_useragent
        self.is_record_headers = is_record_headers
        self.nesss_access_heads_keys = nesss_access_heads_keys
        self.ignore_url = ignore_url

    def make_traceid(self, request) -> None:
        """生成追踪链路 ID、索引值、日志开始记录的时间"""
        request.state.traceid = shortuuid.uuid()
        request.state.trace_links_index = 0
        request.state.start_time = perf_counter()

    def make_token_request(self, request):
        """生成当前请求上下文对象 request"""
        return request_var.set(request)

    def reset_token_request(self, token_request):
        """重置当前请求上下文对象 request"""
        request_var.reset(token_request)

    def filter_request_url(self, request):
        """过滤不需要记录日志的请求 url"""
        path_info = request.url.path
        for item in self.ignore_url:
            if item in path_info:
                return False
        return True

    async def make_request_log_msg(self, request: Request) -> typing.Dict:
        """简化的请求日志信息生成，避免消费流"""
        ip = request.client.host if request.client else "unknown"
        method = request.method
        url = request.url.path

        # 简化的用户代理解析
        user_agent_str = request.headers.get("user-agent", "")
        user_agent = None
        if self.is_record_useragent and user_agent_str:
            try:
                user_agent = parse(user_agent_str)
            except Exception:
                user_agent = None

        log_msg = {
            "traceid": getattr(request.state, "traceid", "unknown"),
            "headers": (
                None
                if not self.is_record_headers
                else (
                    dict(request.headers)
                    if not self.nesss_access_heads_keys
                    else {
                        key: request.headers.get(key, "")
                        for key in self.nesss_access_heads_keys
                    }
                )
            ),
            "useragent": (
                None
                if not self.is_record_useragent or not user_agent
                else {
                    "os": f"{user_agent.os.family} {user_agent.os.version_string}",
                    "browser": f"{user_agent.browser.family} {user_agent.browser.version_string}",
                    "device": {
                        "family": user_agent.device.family,
                        "brand": user_agent.device.brand,
                        "model": user_agent.device.model,
                    },
                }
            ),
            "url": url,
            "method": method,
            "ip": ip,
            "params": {
                "query_params": dict(request.query_params),
                # 不读取 form 和 body，避免消费流
                "form": (
                    "multipart-form-data"
                    if request.headers.get("content-type", "").startswith("multipart/")
                    else None
                ),
                "body": (
                    "binary-data"
                    if request.headers.get("content-type", "").startswith(
                        "application/"
                    )
                    else None
                ),
            },
            "ts": f"{datetime.now():%Y-%m-%d %H:%M:%S%z}",
        }

        return log_msg

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """修复后的中间件调用方法，避免提前消费流"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 创建请求对象但不消费流
        request = StarletteRequest(scope)

        # 过滤需要记录的请求 URL
        if not self.filter_request_url(request):
            await self.app(scope, receive, send)
            return

        # 生成链路 ID
        self.make_traceid(request)
        token_request = self.make_token_request(request)

        try:
            # 生成请求日志信息（不消费流）
            log_msg = await self.make_request_log_msg(request)
            # 写日志信息到文件中
            await async_trace_add_log_record(event_type="request", msg=log_msg)

            # 调用下一个中间件或应用
            await self.app(scope, receive, send)

        finally:
            # 计算响应时间
            end_time = perf_counter()
            response_time = end_time - request.state.start_time

            # 记录响应日志
            response_log = {
                "traceid": request.state.traceid,
                "response_time": f"{response_time:.4f}s",
                "ts": f"{datetime.now():%Y-%m-%d %H:%M:%S%z}",
            }
            await async_trace_add_log_record(event_type="response", msg=response_log)
            self.reset_token_request(token_request)
