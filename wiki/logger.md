# 1 logger

- web 框架的日志系统更多倾向于请求 API 和响应 API 方面的日志，而非业务逻辑的日志
- 请求 API 以及响应 API 的例子如下：

```bash
2025-09-02 17:32:57.638 │ INFO     │ Request Log: {"event_type": "request", "data": {"useragent": {"os": "Mac OS X  10.15.7", "browser": "Chrome  139.0.0", "device": {"family": "Mac", "brand": "Apple", "model": "Mac"}}, "url": "/api/v1/doctor_list", "method": "GET", "ip": "127.0.0.1", "params": {}, "ts": "2025-09-02 17:32:57"}, "remarks": "", "timestamp": "2025-09-02 17:32:57"}

2025-09-02 17:32:57.645 │ INFO     │ Response Log: {"event_type": "response", "data": {"traceid": "EMHPicguazTfj9RN2z2RLK", "response_time": "0.0104s", "ts": "2025-09-02 17:32:57"}, "remarks": "", "timestamp": "2025-09-02 17:32:57"}
```

这是一个 trace 中间件日志链路追踪和响应头的一种实现

对于非语法错误，有响应结果，无论是参数正确返回的响应结果还是参数错误返回的响应结果，均视为 INFO 级别日志，如：

```json
http://127.0.0.1:8000/api/v1/doctor/4123123
{
  "message": "获取医生信息失败: __init__() got an unexpected keyword argument 'code'",
  "success": false,
  "timestamp": 1756805560300,
  "result": null,
  "code": 1000
}

http://127.0.0.1:8000/api/v1/doctor/1
{
  "message": "获取成功",
  "success": true,
  "timestamp": 1756805560300,
  "result": {
    "id": 1,
    "name": "张医生",
    "department": "内科",
    "title": "主任医师",
    "specialty": "心血管疾病",
    "available": true
  },
  "code": 200
}
```

后者是有记录的，但是前者是没有记录的，但是也不影响业务逻辑的正常运行，因此视为 INFO 级别的日志

但是没有业务逻辑的日志，全程用 print 是不好的，所以这个框架仍然添加业务逻辑的日志

logururoute/business_logger.py：业务逻辑日志
logururoute/logger.py：请求 API 以及响应 API 的日志
logururoute/config.py：日志配置，统一关联业务逻辑和 HTTP 请求响应日志

- log/prod：存放的是生产环境的日志，即请求 API 以及响应 API 的日志
- log/dev：存放的是开发环境的日志，即业务逻辑的日志

## DEBUG

- 用于开发、诊断问题，记录最详细的信息

## INFO

- 确认程序按预期运行，记录关键、常规的业务流程

## WARNING

- 发生预期之外的情况，或者未来可能会出现问题，当前不影响程序的执行，但是需要注意

## ERROR

- 发生严重的错误，导致某个功能无法完成，但是程序仍然可以正常运行，并且程序可能可以自动恢复错误

## CRITICAL

- 最高级别错误，导致整个程序无法运行，需要人工干预

## 使用方式

```python
from exts.logururoute.business_logger import logger

logger.info("开始获取可预约医生列表")
logger.warning("测试警告")
logger.error("测试错误")
logger.debug("测试调试")
logger.critical("测试严重")
```

它会同时在控制台和文件中输出日志，文件路径为 `log/prod/YYYY-MM-DD_arch.log`，日志格式为 time:YYYY-MM-DD HH:mm:ss.SSS | level | name:function:line | message"