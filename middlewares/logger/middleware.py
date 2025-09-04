from contextvars import ContextVar
from fastapi import Request
import shortuuid
from starlette.types import ASGIApp, Receive, Scope, Send
from user_agents import parse
from urllib.parse import parse_qs
from datetime import datetime
import typing
from time import perf_counter

from exts.requestvar.bing import bind_contextvar
from exts.logururoute.config import async_trace_add_log_record

request_var: ContextVar[Request] = ContextVar("request")
request: Request = bind_contextvar(request_var)


class LogerMiddleware:
    def __init__(
        self,
        *,
        app: ASGIApp,
        is_record_useragent=False,  # 是否记录用户 UA 信息
        is_record_headers=False,
        nesss_access_heads_keys=[],  # 日志记录哪一部分关键请求信息
        ignore_url: typing.List = ["/favicon.ico", "websocket"],
    ) -> None:
        self.app = app
        self.is_record_useragent = is_record_useragent
        self.is_record_headers = is_record_headers
        self.nesss_access_heads_keys = nesss_access_heads_keys
        self.ignore_url = ignore_url

    def make_traceid(self, request) -> None:
        """
        生成追踪链路 ID、索引值、日志开始记录的时间
        :param request: 请求对象
        :return: 追踪链路 ID
        """
        request.state.traceid = shortuuid.uuid()
        # 追踪索引序号
        request.state.trace_links_index = 0
        # 追踪 ID
        request.state.traceid = shortuuid.uuid()
        # 计算时间
        request.state.start_time = perf_counter()

    def make_token_request(self, request):
        """
        生成当前请求上下文对象 request
        :param request: 请求对象
        :return:

        ---
        对request_var: ContextVar[Request] = ContextVar("request")进行当前对象的设置，
        以便后续全局代理对象获取到当前设置的对象
        """
        return request_var.set(request)

    def reset_token_request(self, token_request):
        """
        重置当前请求上下文对象 request
        :param token_request: 请求对象
        :return:
        """
        request_var.reset(token_request)

    async def get_request_body(self, request) -> typing.AnyStr:
        """
        对请求参数有 body 的数据进行读取
        """
        body = None
        try:
            body_bytes = await request.body()
            if body_bytes:
                try:
                    body = await request.json()
                except:
                    pass
                    if body_bytes:
                        try:
                            body = body_bytes.decode("utf-8")
                        except:
                            body = body_bytes.decode("gb2312")
        except:
            pass
        request.state.body = body
        return body

    def filter_request_url(self, request):
        path_info = request.url.path
        # 过滤不需要记录日志的请求 url
        for item in self.ignore_url:
            if item in path_info:
                return False
        return True

    async def make_request_log_msg(self, request) -> typing.Dict:
        """
        读取当前对象 request 的请求信息，并生成日志信息
        """
        # 从当前请求中获取具体的客户端信息
        ip, method, url = request.client.host, request.method, request.url.path
        # 解析请求提交的表单信息
        try:
            body_form = await request.form()
        except:
            body_form = None

        # 记录当前提交的 body 数据，用于下文提取
        body = await self.get_request_body(request)

        # 从头部里获取对应的请求头信息
        try:
            user_agent = parse(request.headers["User-Agent"])
            # 提取 UA 信息
            browser = user_agent.browser.version
            if len(browser) >= 2:
                browser_major, browser_minor = browser[0], browser[1]
            else:
                browser_major, browser_minor = 0, 0
            # 提取OS 信息
            user_os = user_agent.os.version
            if len(user_os) >= 2:
                os_major, os_minor = user_os[0], user_os[1]
            else:
                os_major, os_minor = 0, 0

            log_msg = {
                "headers": (
                    None
                    if not self.is_record_headers
                    else (
                        [
                            request.headers.get(i, "")
                            for i in self.nesss_access_heads_keys
                        ]
                        if self.nesss_access_heads_keys
                        else None
                    )
                ),
                # 记录请求 URL 信息
                "useragent": (
                    None
                    if not self.is_record_useragent
                    else {
                        "os": "{}  {}".format(
                            user_agent.os.family, user_agent.os.version_string
                        ),
                        "browser": "{}  {}".format(
                            user_agent.browser.family, user_agent.browser.version_string
                        ),
                        "device": {
                            "family": user_agent.device.family,
                            "brand": user_agent.device.brand,
                            "model": user_agent.device.model,
                        },
                    }
                ),
                "url": url,
                # 记录请求方法
                "method": method,
                # 记录请求来源 ip
                "ip": ip,
                # 记录请求提交的参数信息
                "params": {
                    "query_params": parse_qs(str(request.query_params)),
                    "from": body_form,
                    "body": body,
                },
                "ts": f"{datetime.now():%Y-%m-%d %H:%M:%S%z}",
            }
        except:
            log_msg = {
                "headers": (
                    None
                    if not self.is_record_headers
                    else (
                        [
                            request.headers.get(i, "")
                            for i in self.nesss_access_heads_keys
                        ]
                        if self.nesss_access_heads_keys
                        else None
                    )
                ),
                "url": url,
                "method": method,
                "ip": ip,
                "params": {
                    "query_params": parse_qs(str(request.query_params)),
                    "from": body_form,
                    "body": body,
                },
                "ts": f"{datetime.now():%Y-%m-%d %H:%M:%S%z}",
            }

        # 如果请求头信息需要记录且数据为空，删除该请求参数项的日志信息
        if "headers" in log_msg and not log_msg["headers"]:
            log_msg.pop("headers")
        if log_msg["params"]:
            if (
                "query_params" in log_msg["params"]
                and not log_msg["params"]["query_params"]
            ):
                log_msg["params"].pop("query_params")
            if "from" in log_msg["params"] and not log_msg["params"]["from"]:
                log_msg["params"].pop("from")
            if "body" in log_msg["params"] and not log_msg["params"]["body"]:
                log_msg["params"].pop("body")
        return log_msg

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        请求进来时，会创建当前的请求request对象
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 读取一次
        receive_ = await receive()

        # 定义新协程函数并返回 receive 结果
        async def receive():
            return receive_

        # 创建需要解析的参数
        request = Request(scope, receive=receive)

        # 过滤需要记录的请求 URL
        if self.filter_request_url(request):
            # 生成链路 ID
            self.make_traceid(request)
            token_request = self.make_token_request(request)
            # 生成请求日志信息
            log_msg = await self.make_request_log_msg(request)
            # 写日志信息到文件中
            await async_trace_add_log_record(event_type="request", msg=log_msg)
            try:
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
                await async_trace_add_log_record(
                    event_type="response", msg=response_log
                )
                self.reset_token_request(token_request)
        else:
            await self.app(scope, receive, send)
