# FastAPI AI 时代脚手架

> **专为 AI 辅助编程、零配置的 FastAPI 脚手架**

用户只需用自然语言与 AI 提需求，例如："在这个基础上，给我加个用户订单模块"。AI 能顺着已有基础设施直接完成功能，不用担心配置、环境和工程规范，只需专注于业务逻辑。

## 解决了什么问题

| 问题 | 解决方案 |
|---|---|
| 如何连数据库 | 预装全套异步 MySQL + SQLModel |
| 事务怎么管 | `depends_get_db_session_with_transaction` 自动提交和回滚 |
| 权限怎么做 | JWT + Argon2 密码哈希，拿来即用 |
| 多环境配置 | Pydantic Settings + `.env` 方案 |
| 响应格式统一 | `JsonRoute` 自动包装 `{success, code, data, timestamp}` |

## 快速开始

### 环境要求

- Python 3.9+
- MySQL 8.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 数据库配置

```bash
cp .env.example .env
# 修改 .env 中的 DATABASE_URL
```

### 初始化数据库

首次拉取代码或新环境部署时，运行一次：

```bash
python dev_tools/init_alembic.py
```

该脚本会自动完成：
- 检测并创建 MySQL 数据库（无需手动执行 `CREATE DATABASE`）
- 生成或应用 Alembic 迁移版本，建好所有数据表

### 后续表结构变更

修改 `db/models.py` 后，运行：

```bash
python dev_tools/migration_db.py
```

会生成迁移脚本并在人工确认后应用。详细操作见 [docs/数据库迁移操作手册.md](docs/数据库迁移操作手册.md)。

### 启动应用

```bash
python main.py
```

访问 API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 项目结构

```
.
├── app.py                  # 应用入口，注册路由和中间件
├── main.py                 # uvicorn 启动入口
├── routers/                # 业务路由（每个文件 = 一个完整模块）
│   ├── example.py          # 设计单位模块：Schemas + 扁平 Router
│   └── user.py             # 用户模块：Schemas + 扁平 Router
├── db/
│   ├── models.py           # SQLModel 数据库表定义
│   └── database.py         # 异步连接池 + 依赖注入
├── alembic/                # Alembic 迁移目录
│   ├── env.py              # 迁移环境配置（已绑定 SQLModel.metadata）
│   └── versions/           # 迁移版本脚本
├── dev_tools/
│   ├── init_alembic.py     # 首次初始化：建库 + 应用迁移
│   └── migration_db.py     # 日常变更：生成并应用迁移（带人工审查）
├── exts/
│   ├── route.py            # JsonRoute：自动包装统一响应格式
│   ├── auth.py             # JWT 认证依赖注入
│   ├── exceptions/
│   │   └── exception_handler.py  # 全局异常处理
│   └── logururoute/        # 结构化日志
├── utils/
│   ├── jwt.py              # JWT 工具函数
│   ├── password.py         # Argon2 密码哈希
│   └── type.py             # Pydantic 自定义类型
├── config/
│   └── settings.py         # Pydantic Settings 配置
└── tests/
    ├── test_example.py     # 设计单位黑盒集成测试
    └── test_user.py        # 用户接口黑盒集成测试
```

## 如何新增一个业务模块

AI 只需在 `routers/` 目录下新建一个文件，按以下结构编写：

```python
# routers/order.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from exts.route import JsonRoute
from db.database import depends_get_db_session, depends_get_db_session_with_transaction
from db.models import Order  # 在 db/models.py 中先定义好模型

# ======================== Schemas ========================
class OrderCreateRequest(BaseModel):
    product: str
    quantity: int

class OrderResponse(BaseModel):
    id: int
    product: str
    quantity: int
    model_config = {"from_attributes": True}

# ======================== Router ========================
router = APIRouter(prefix="/api", tags=["订单"], route_class=JsonRoute)

@router.post("/order")
async def create_order(
    payload: OrderCreateRequest,
    db: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    order = Order(**payload.model_dump())
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)
```

然后在 `app.py` 中添加两行：
```python
from routers.order import router as order_router
app.include_router(order_router)
```

## 响应格式

所有接口统一返回标准格式（由 `JsonRoute` 自动包装）：

**成功：**
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": { ... },
  "timestamp": 1678886400000
}
```

**失败（直接 `raise HTTPException`）：**
```json
{
  "success": false,
  "code": 404,
  "message": "资源不存在",
  "data": null,
  "timestamp": 1678886400000
}
```

## 技术栈

| 组件 | 技术 |
|---|---|
| Web 框架 | FastAPI |
| 数据库 | MySQL + SQLModel + SQLAlchemy (async) |
| 异步驱动 | aiomysql |
| 配置管理 | Pydantic Settings |
| 日志 | Loguru |
| 密码哈希 | Argon2 |
| JWT | PyJWT |
| 测试 | pytest + httpx |
