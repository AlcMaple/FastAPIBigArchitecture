# FastAPI 医疗管理系统

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

```env
DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/arch_db
```

### 启动应用

```bash
python main.py
```

应用启动后访问：

* API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)
* 健康检查：[http://localhost:8000/health](http://localhost:8000/health)

## 📁 项目结构

```
FastAPIBigArchitecture/
├── app.py                  # 主应用入口文件
├── main.py                 # 启动文件
├── requirements.txt        # Python 依赖包
├── README.md              # 项目说明文档
│
├── apis/                   # API 路由模块
│   ├── __init__.py        # 路由注册和导出
│   ├── doctor/            # 医生相关功能模块
│   │   ├── __init__.py    # 模块导出
│   │   ├── api/           # API 层 - 路由处理
│   │   │   ├── doctor.py  # 医生相关路由
│   │   ├── services/      # 业务逻辑层
│   │   │   ├── doctor.py     # 医生业务逻辑
│   │   │   ├── schedule.py   # 排班业务逻辑
│   │   │   └── appointment.py # 预约业务逻辑
│   │   ├── repository/    # 数据访问层
│   │   │   ├── doctor.py     # 医生数据操作
│   │   │   ├── schedule.py   # 排班数据操作
│   │   │   └── appointment.py # 预约数据操作
│   │   ├── schemas/       # 数据模型层
│   │   │   ├── doctor.py     # 医生请求/响应模型
│   │   │   ├── schedule.py   # 排班请求/响应模型
│   │   │   └── appointment.py # 预约请求/响应模型
│   │   └── dependencies/  # 依赖注入
│   └── hospital/          # 医院相关功能模块
│
├── db/                    # 数据库相关
│   ├── __init__.py       # 数据库初始化导出
│   ├── database.py       # 数据库连接配置
│   ├── init_db.py        # 数据库表初始化
│   └── models.py         # SQLModel 数据库模型定义
│
├── config/               # 配置管理
│   ├── __init__.py      # 配置导出
│   └── settings.py      # 应用配置类
│
├── exts/                # 扩展组件
│   ├── __init__.py      # 扩展组件导出
│   ├── responses/       # 统一响应格式
│   │   ├── __init__.py
│   │   └── json_response.py # Success/Fail 响应类
│   ├── exceptions/      # 异常处理
│   │   ├── __init__.py
│   │   └── handlers.py  # 异常处理器
│   ├── logururoute/     # 日志路由
│   │   ├── __init__.py
│   │   └── logger.py    # 日志配置
│   └── requestvar/      # 请求变量
│       ├── __init__.py
│       └── bing.py      # 请求上下文变量
│
├── middlewares/         # 中间件
│   ├── __init__.py     # 中间件导出
│   └── loger/          # 日志中间件
│       ├── __init__.py
│       └── middleware.py # 请求日志记录中间件
│
├── utils/              # 工具函数
│   ├── __init__.py    # 工具函数导出
│   └── datetime_helper.py # 日期时间处理工具
│
├── log/               # 日志文件存储
│   ├── error_*.log    # 错误日志
│   └── info_*.log     # 信息日志
│
├── static/            # 静态文件
└── plugins/           # 插件扩展
    └── __init__.py
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

### 响应格式

所有 API 响应统一使用 Success/Fail 格式：

```python
# 成功响应
Success(result=data)

# 失败响应
Fail(message="错误信息")
```

## API 示例

### 获取医生列表

```http
GET /api/v1/doctor_list
```

### 创建预约

```http
POST /api/v1/appointments
Content-Type: application/json

{
    "doctor_id": 1,
    "patient_name": "张三",
    "patient_phone": "13800138000",
    "appointment_date": "2024-01-15",
    "appointment_time": "09:00"
}
```

### 获取医生排班

```http
GET /api/v1/doctors/1/schedules?date=2024-01-15
```

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

## 相关链接

* [FastAPI 官方文档](https://fastapi.tiangolo.com/)
* [SQLModel 文档](https://sqlmodel.tiangolo.com/)
* [Pydantic 文档](https://pydantic-docs.helpmanual.io/)

## 许可证

此项目遵循 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。