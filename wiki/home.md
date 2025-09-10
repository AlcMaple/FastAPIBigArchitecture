# Home

- 这是一个基于FastAPI的大型架构项目，适用于中大型项目的开发，如果你是分布式系统还需再考虑一下
- 这个项目对于普通公司、个人开发者以及普通团队开发是足够的，但是不限于跨省跨地区级分布式系统开发的情况，也就是如果你想把它分成各个子模块到各个区域单独开发，那就需要考虑一下如何划分子模块、如何进行服务化、如何进行数据库设计、如何进行缓存设计、如何进行消息队列设计、如何进行微服务架构设计等等，这些都是需要考虑的事情

- 本框架提供了两种主流方式：
  - fastapi + mysql + sqlmodel
  - fastapi + json

## mysql方案

- 如果你采用 mysql 的方案，那么要如何使用呢？
- 首先本框架默认你已经有了基础的环境：mysql 环境、python 环境等，如果你没有，请先安装好相关环境
- 虽然推荐的环境要求如下：
    - Python 3.8+
    - MySQL 8.0+

- 但是使用的时候我推荐你与我有相同的环境配置

### python安装

如果是 Windows 用户
直接下载安装包：[Python 3.9.13 Windows 安装包](https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe)
或访问官网：https://www.python.org/downloads/release/python-3913/
安装注意事项：
- 勾选 "Add Python to PATH"
- 选择 "Install for all users"

---

如果是 macOS 用户
下载安装包：[Python 3.9.13 macOS 安装包](https://www.python.org/ftp/python/3.9.13/python-3.9.13-macosx10.9.pkg)

---

如果是 Linux 用户
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv

# CentOS/RHEL
sudo yum install python39 python39-pip
```

安装完成后，验证安装环境
```bash
python --version
# 输出：Python 3.9.x
```

---

对于 Windows 和 macos 用户，更加推荐使用 conda 来进行管理 python
```bash
conda create -n arch python==3.9.19 -y
conda activate arch
python --version
```

### mysql安装

如果是 Windows 用户
下载[MySQL Installer：MySQL 8.0.34 Windows](https://dev.mysql.com/downloads/installer/)
注意：版本的重要性不大，下载最新的就行，macOS 和 Linux 同理

---

如果是 macOS 用户
下载DMG文件：[MySQL 9.0.1 macOS](https://dev.mysql.com/downloads/mysql/)

---

如果是 Linux 用户
```bash
# Ubuntu/Debian
wget https://dev.mysql.com/get/mysql-apt-config_0.8.29-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.29-1_all.deb
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
```

mysql 安装完成后，进行 mysql 的登录验证
```bash
# 登录MySQL
mysql -u root -p

# 退出
EXIT;
```
自此项目环境搭建完成，接下来开始安装依赖和运行项目

### 安装依赖

```bash
pip install -r requirements.txt
```

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

- 启动成功后，访问 API 文档进行部分接口的测试（简单测试即可，比如测试一些不需要传参数的，看到输出结果即可
- 然后退出应用，尝试运行：pytest testcase/test_sync_api.py -v
- 如果也能看到测试的正常运行，那么你的项目就算成功搭建了

## 操作框架

- 项目结构：
```bash
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

- 可以看到框架的项目结构如上，操作流程如下（大多数情况下可以参照提供的模版来完成二次开发）

### 更新启动端口

- 可以通过 main.py来自定义你的端口号，port=8000 是默认值，可以修改为其他端口号，它将会运行到你设置的端口号（注意不要端口冲突

### API文档

- fastapi 有自带的 api 文档，你可以修改它的标题描述等信息，通过 app.py
```python
# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    description=" FastAPI 管理系统API",
    version="1.0.0",
    lifespan=lifespan,
)
```
你可以修改它的描述已经版本号为自己的版本，标题则需要通过 config/settings.py 来修改

控制台的日志的使用方式可以参照[logger]()来了解如何使用

### utils

- 这里存放一些工具类，比如时间处理的 datetime_helper.py

### db

- 这里你需要了解 database.py的两个方法：depends_get_db_session 和 depends_get_db_session_with_transaction
    - > 也就是如果你是查询操作使用前者作为 session 会话，如果是增删改操作使用后者作为 session 会话
    - > 具体使用的模板 apis/doctor/api/doctor.py 中的 create_doctor 和 update_doctor 就是使用了后者，而 get_doctor_list 和 get_all_doctors 则使用了前者
- 然后就是 models.py，这个是你需要编写的，里面需要定义你的数据表结构，比如 doctor 表， appointment 表，你只需要参照已有的模型来定义即可，你会学会怎么定义的

- 当你定义好后，启动项目会自动创建你所定义的所有数据表，前提是你已经创建好了数据库

### config

- 这里存放的是你项目的配置项，你无需修改，它是通过.env来读取配置进行重写的，你只需要参照.env.example来创建自己的配置文件即可

### apis

- apis 层主要分了五层架构，实际上使用更多的是四层
- 在 api 里面定义你的接口，在 `api/__init__.py` 里导入你定义的接口文件，进行路由分组
- api 层会调用 services 层
- services 层定义了具体的业务逻辑，比如 doctor 层的 doctor.py 定义了 doctor 相关的业务逻辑，比如创建 doctor，获取 doctor 列表等，它会调用 repository 层
- repository 层定义了数据访问层，比如 appointment.py 定义了 appointment 相关的数据库操作，比如创建 appointment，获取 appointment 列表等
- schemas 层定义了数据请求和响应的参数，用于封装请求和响应的参数，比如 appointment.py 定义了 appointment 请求和响应的参数，用于创建 appointment 和获取 appointment 列表
- dependencies 层定义了依赖，比如 doctor.py 定义了 doctor 相关的依赖，比如获取当前登录的用户信息等

---

- 具体它们的关系以及如何使用，你需要通过一个接口去查看它们的关系，然后尝试编写出自己的接口，这样你就会了解到一个 api是如何编写的了
- 最外层的`__init__.py`则是将你的接口导出去，供 app.py 导入使用，在你编写好 apis 层的内容后，你还需要在 app.py里面导入你的路由
- 这样你的路由才会真正的注册成功，并且能够通过 api 文档去访问查看你的接口

```python
# 导入路由分组
from apis import router_doctor, router_appointment

# 注册路由分组
app.include_router(router_doctor)
app.include_router(router_appointment)
```

### testcase

- 这里存放的是测试用例，你可以在这里编写测试用例，然后运行 pytest 命令来运行测试用例，测试用例的编写可以参照已有的测试用例，比如 `test_sync_api.py`
- 你需要安装 pytest 库，然后在项目根目录下运行 `pytest` 命令，它会自动找到 testcase 目录下的所有测试用例，并运行测试用例
- 注意：你只需要在 testcase 创建以 `test_`开头 或者 `_test`结尾的文件，它才会被 pytest 识别为测试用例，其他文件不会被识别
- 注意：你不需要编写 conftest.py文件，你只需要参考 `test_sunc_api.py` 中的写法，创建自己的测试文件案例即可

## json方案

- 如果你采用 json 的方案，那么要如何使用呢？
- 在使用上基本没什么区别，甚至更加简单
- 在 mysql 方案上提到的这里不会再提了，如果你想了解更多，可以查看 mysql 方案