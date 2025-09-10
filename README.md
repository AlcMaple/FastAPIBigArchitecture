# FastAPI Web 框架

基于 FastAPI 的个人服务项目框架，采用分层架构设计

## 快速开始

### 环境要求
- Python 3.8+
- MySQL 8.0+

### 安装依赖
```bash
pip install -r requirements.txt
````

### 数据库配置

1. 创建 MySQL 数据库：

```sql
CREATE DATABASE arch_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 复制环境配置文件：

```bash
cp .env.example .env
```

3. 修改 `.env` 文件中的数据库连接信息：

```bash
DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/arch_db
```

4. 如果需要测试的话，还需要创建测试数据库：

```sql
CREATE DATABASE arch_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. 修改 `.env` 文件中的测试数据库连接信息：

```bash
TEST_DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/arch_test_db
```

### 启动应用

```bash
python main.py
```

应用启动后访问：

* API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)

## 项目结构

```
FastAPIBigArchitecture/
├── apis
│   ├── doctor
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   └── doctor.py
│   │   ├── dependencies
│   │   ├── repository
│   │   │   ├── appointment.py
│   │   │   ├── doctor.py
│   │   │   └── schedule.py
│   │   ├── schemas
│   │   │   ├── appointment.py
│   │   │   ├── doctor.py
│   │   │   └── schedule.py
│   │   └── services
│   │       ├── appointment.py
│   │       ├── doctor.py
│   │       └── schedule.py
│   ├── hospital
│   └── __init__.py
├── config
│   └── settings.py
├── db
│   ├── database.py
│   ├── init_db.py
│   └── models.py
├── exts
│   ├── exceptions
│   │   └── handlers.py
│   ├── logururoute
│   │   ├── business_logger.py
│   │   └── config.py
│   ├── requestvar
│   │   └── bing.py
│   └── responses
│       └── json_response.py
├── middlewares
│   └── logger
│       └── middleware.py
├── plugins
├── static
├── testcase
│   ├── conftest.py
│   └── test_sync_api.py
├── utils
│   └── datetime_helper.py
├── wiki
│   ├── db.md
│   ├── logger.md
│   └── test.md
├── .env.example
├── .gitignore
├── app.py
├── CLAUDE.md
├── main.py
├── pytest.ini
├── README.md
└── requirements.txt
```

## 架构设计

### 分层架构

项目采用经典的五层架构模式：

1. **API 层 (`api/`)** - 处理 HTTP 请求和响应

   * 路由定义和请求验证
   * 调用业务逻辑层
   * 异常处理和响应格式化

2. **业务逻辑层 (`services/`)** - 核心业务逻辑

   * 业务规则实现
   * 数据处理和验证
   * 调用数据访问层

3. **数据访问层 (`repository/`)** - 数据库操作

   * 数据库查询和操作
   * 数据映射和转换
   * 事务管理

4. **数据模型层 (`schemas/`)** - 数据传输对象

   * 请求/响应模型定义
   * 数据验证规则
   * 序列化/反序列化

5. **依赖注入层 (`dependencies/`)** - 依赖注入管理

   * 依赖注入管理
   * 依赖注入的配置

### 核心组件

#### 数据库 (`db/`)

* **database.py**: 异步 MySQL 连接池配置
* **models.py**: SQLModel 数据库表定义
* **init\_db.py**: 自动创建数据库表

#### 配置管理 (`config/`)

* **settings.py**: 基于 Pydantic 的配置类
* 支持环境变量和 `.env` 文件
* 数据库连接池配置

#### 扩展组件 (`exts/`)

* **responses/**: 统一的 Success/Fail 响应格式
* **exceptions/**: 全局异常处理
* **logururoute/**: 结构化日志配置

#### 中间件 (`middlewares/`)

* **loger/**: 请求/响应日志记录
* 自动记录 API 调用信息
* 支持忽略特定 URL

## 数据库模型

### 核心实体

* **Doctor**: 医生信息（姓名、科室、职称、专长等）
* **Schedule**: 医生排班（日期、时间段、最大接诊数）
* **Appointment**: 预约记录（患者信息、预约时间、状态）
* **Patient**: 患者信息（姓名、联系方式、病史等）

### 关系设计

* 医生 ↔ 排班：一对多关系
* 医生 ↔ 预约：一对多关系
* 患者 ↔ 预约：一对多关系

## 开发规范

### 模块组织

每个功能模块遵循固定的目录结构：

```
module_name/
├── __init__.py        # 模块导出
├── api/              # API 路由层
├── services/         # 业务逻辑层
├── repository/       # 数据访问层
├── schemas/          # 数据模型层
└── dependencies/     # 依赖注入
```

exts/ 目录用于存放自定义扩展组件，如**全局**日志、请求上下文变量等。

plugs/ 目录用于存放插件扩展，如**自定义**插件、第三方插件等。

根目录开发规范：

* 可以添加自定义的一些相关模块，如wxchatsdk（微信支付SDK）

### 代码规范

* 使用 Python 类型注解
* 异步编程模式（async/await）
* 依赖注入模式
* 统一错误处理
* RESTful API 设计

## 开发命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python main.py

# 查看 API 文档
# 访问 http://localhost:8000/docs
```

## 技术栈

* **Web 框架**: FastAPI
* **数据库**: MySQL + SQLModel + SQLAlchemy
* **异步驱动**: aiomysql
* **配置管理**: Pydantic Settings
* **日志记录**: Loguru
* **API 文档**: Swagger UI / ReDoc
* **类型检查**: Python Type Hints