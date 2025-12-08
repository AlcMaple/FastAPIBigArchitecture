# 1.3 Exception

## ErrorCode 枚举（错误码定义）

**代码位置**: exts/exceptions/error_code.py

- 所有的错误码和默认信息全部在这里进行配置和维护

## ApiException 统一异常类

**代码位置**: exts/exceptions/api_exception.py

```python
from exts.exceptions import ApiException, ErrorCode

# 基本用法：使用默认消息
raise ApiException(ErrorCode.NOT_FOUND)
# 返回: {"success": false, "code": 4040, "message": "请求的资源不存在"}

# 携带额外数据
raise ApiException(
    ErrorCode.VALIDATION_ERROR,
    "数据验证失败",
    data={"field": "email", "error": "邮箱格式错误"}
)
# 返回: {
#   "success": false,
#   "code": 1010,
#   "message": "数据验证失败",
#   "data": {"field": "email", "error": "邮箱格式错误"}
# }
```

## Success 成功响应类

**代码位置**: exts/responses/api_response.py

```python
from exts.responses import Success

# 基本用法
return Success()
# 返回: {"success": true, "code": 200, "message": "操作成功", "data": null}

# 携带数据
return Success(data={"user_id": 123, "name": "张三"})
# 返回: {"success": true, "code": 200, "message": "操作成功", "data": {...}}

# 自定义消息
return Success(data=user, message="用户信息获取成功")
# 返回: {"success": true, "code": 200, "message": "用户信息获取成功", "data": {...}}
```

## 全局异常处理器

**代码位置**: exts/exceptions/exception_handler.py

- 自动捕获所有异常并转换为统一格式：

| 异常类型                 | 转换为               | 说明                       |
| ------------------------ | -------------------- | -------------------------- |
| `ApiException`           | `Error` 响应         | 业务异常（开发者主动抛出） |
| `RequestValidationError` | `Error` (code: 1001) | Pydantic 参数校验失败      |
| `StarletteHTTPException` | 根据状态码转换       | HTTP 异常（404, 405 等）   |
| `Exception`              | `Error` (code: 5100) | 所有未捕获的异常           |

## 开发者分层使用

### Schemas 层（数据模型）

- 使用 Pydantic 进行参数校验

**Pydantic 校验失败时**：

- 自动转换为 `ParameterException` (code: 1001)
- 错误详情包含在 `data` 字段中

---

### Repository 层（数据访问）

**职责**：

- 执行数据库操作
- 返回字典、列表或 `None`
- **不做业务判断**
- **不抛出业务异常**（数据库异常自然上抛）

```python
class UserRepository:
    @staticmethod
    async def get_by_id(db_session, user_id: int) -> Optional[Dict]:
        """
        获取用户信息

        Returns:
            Dict: 用户信息，如果不存在返回 None
        """
        result = await db_session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        # Repository 层：不做判断，返回 None
        if not user:
            return None

        return {
            "user_id": user.user_id,
            "name": user.name,
        }

    @staticmethod
    async def create(db_session, user_data: Dict) -> Dict:
        """
        创建用户

        Raises:
            IntegrityError: 数据库约束错误（自然上抛）
        """
        user = User(**user_data)
        db_session.add(user)
        await db_session.flush()

        return {
            "user_id": user.user_id,
            **user_data
        }
```

---

### Service 层（业务逻辑）

**职责**：

- 调用 Repository 获取数据
- 进行业务规则验证
- **使用 `raise ApiException(ErrorCode.XXX)` 抛出异常**
- 返回业务数据（不返回响应对象）

```python
from exts.exceptions.error_code import ErrorCode
from exts.exceptions.api_exception import ApiException

class UserService:
    @staticmethod
    async def get_user_detail(db_session, user_id: int) -> Dict:
        """
        获取用户详情

        Raises:
            ApiException: 用户不存在时抛出
        """
        # 调用 Repository
        user = await UserRepository.get_by_id(db_session, user_id)

        # Service 层判断并抛出异常
        if not user:
            raise ApiException(ErrorCode.USER_NOT_FOUND, f"用户ID {user_id} 不存在")

        return user

    @staticmethod
    async def create_user(db_session, user_request) -> Dict:
        """
        创建用户

        Raises:
            ApiException: 业务验证失败或数据库错误
        """
        try:
            user_data = user_request.dict()
            user = await UserRepository.create(db_session, user_data)
            return user

        except IntegrityError as e:
            # 捕获数据库异常并转换为业务异常
            if "phone" in str(e):
                raise ApiException(
                    ErrorCode.USER_ALREADY_EXISTS,
                    f"手机号 {user_request.phone} 已被使用"
                )
            raise ApiException(ErrorCode.DATABASE_ERROR, "创建用户失败")
```

**常见场景**：

```python
# 1. 认证检查
if not current_user:
    raise ApiException(ErrorCode.UNAUTHORIZED, "请先登录")

# 2. 权限检查
if current_user.role != "admin":
    raise ApiException(ErrorCode.FORBIDDEN, "仅管理员可操作")

# 3. 资源不存在
if not user:
    raise ApiException(ErrorCode.NOT_FOUND, "用户不存在")

# 4. 参数验证
if quantity <= 0:
    raise ApiException(ErrorCode.PARAMETER_ERROR, "数量必须大于0")

# 5. 业务规则验证
if product["stock"] < quantity:
    raise ApiException(
        ErrorCode.INSUFFICIENT_STOCK,
        f"库存不足，当前库存: {product['stock']}"
    )

# 6. 携带额外数据
raise ApiException(
    ErrorCode.VALIDATION_ERROR,
    "数据验证失败",
    data={"errors": validation_errors}
)
```

---

### API 层（路由处理）

**职责**：

- 接收请求参数
- 调用 Service 层
- **返回 `Success` 响应**
- **不捕获异常**（全局处理器会自动处理）

```python
from fastapi import APIRouter, Depends, Path
from exts.responses.api_response import Success
from db.database import depends_get_db_session, depends_get_db_session_with_transaction

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("/{user_id}", summary="获取用户详情")
async def get_user_detail(
    user_id: int = Path(..., description="用户ID"),
    db_session: AsyncSession = Depends(depends_get_db_session),
):
    """
    API 层只需要:
    1. 调用 Service
    2. 返回 Success
    3. 不捕获异常
    """
    user = await UserService.get_user_detail(db_session, user_id)
    return Success(data=user)

@router.post("", summary="创建用户")
async def create_user(
    user_request: UserCreateRequest,
    db_session: AsyncSession = Depends(depends_get_db_session_with_transaction),
):
    """创建用户（自定义成功消息）"""
    user = await UserService.create_user(db_session, user_request)
    return Success(data=user, message="用户创建成功")
```

---

## 扩展错误码

- 场景：新增"订单"相关业务

**第 1 步**: 在 `ErrorCode` 枚举中添加（只需修改这一处）

```python
# exts/exceptions/error_code.py

class ErrorCode(Enum):
    # ... 现有错误码

    # 订单相关 (3500-3599)
    ORDER_NOT_FOUND = (3501, "订单不存在")
    ORDER_ALREADY_PAID = (3502, "订单已支付")
    ORDER_EXPIRED = (3503, "订单已过期")
    ORDER_AMOUNT_MISMATCH = (3504, "订单金额不匹配")
```

**第 2 步**: 直接在业务代码中使用

```python
# Service 层
from exts.exceptions import ApiException, ErrorCode

class OrderService:
    @staticmethod
    async def pay_order(db_session, order_id: int, amount: float):
        order = await OrderRepository.get_by_id(db_session, order_id)

        if not order:
            raise ApiException(ErrorCode.ORDER_NOT_FOUND)

        if order["status"] == "paid":
            raise ApiException(ErrorCode.ORDER_ALREADY_PAID)

        if order["amount"] != amount:
            raise ApiException(
                ErrorCode.ORDER_AMOUNT_MISMATCH,
                f"订单金额 {order['amount']}，支付金额 {amount}"
            )

        # 执行支付逻辑
        ...
```

**完成**！无需创建新的异常类或响应类。

---

## 响应格式

### 成功响应

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "user_id": 1,
    "name": "张先生"
  },
  "timestamp": 1678886400000
}
```

### 错误响应

```json
{
  "success": false,
  "code": 3201,
  "message": "用户 ID 999 不存在",
  "data": null,
  "timestamp": 1678886400000
}
```

### 参数校验错误响应

```json
{
  "success": false,
  "code": 1001,
  "message": "参数 'phone' string does not match regex",
  "data": {
    "errors": [
      {
        "loc": ["body", "phone"],
        "msg": "string does not match regex \"^1[3-9]\\d{9}$\"",
        "type": "value_error.str.regex"
      }
    ]
  },
  "timestamp": 1678886400000
}
```

---
