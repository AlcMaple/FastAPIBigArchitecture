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

- log/prod：存放的是生产环境的日志，即请求 API 以及响应 API 的日志
- log/dev：存放的是开发环境的日志，即业务逻辑的日志