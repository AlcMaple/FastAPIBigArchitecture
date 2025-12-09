# 1.2 Test

Test 的实现位于 `testcase/***.py` 文件中

conftest.py 是 Test 的配置文件，本框架的测试是使用独立的数据库进行测试，不影响项目中使用的数据库，并且每次测试前都会清空并初始化所有的数据

需要手动编写测试文件的话只需要在 `testcase/*`中添加测试文件即可，必须是 `test_`开头或者`_test`作为结尾

本框架提供了测试文件供参考，使用者只需要模仿里面的写法完成自己的接口测试即可

## 测试方案

- 测试不是目的，而是保障质量和信心的手段，即测试成功不代表你的项目一点 bug 都没有
- 金字塔原理

## Mock 数据

- Mock 数据是指假数据，它可以是请求的假数据，也可以是响应的假数据

## 单元测试

- 它是金字塔的底层，通常是一个函数或一个类的方法的逻辑是否正确
- 特点：
  - 快：**不涉及网络、数据库**、文件系统等外部依赖
  - 隔离：只关注一个单元，所有外部依赖都应该被 Mock（模拟）
  - 精确：一旦失败，能立刻定位到是哪个函数的逻辑出了问题
- 示例：

  - 复杂的计价函数
  - 数据转换工具
  - 自定义的权限判断逻辑
  - 项目中各种辅助函数（Utils）
  - 还有其他独立于框架外的核心代码

- 单元测试,保证了你代码的“零件”是好的，但不能保证“组装”起来能用

- 下面给出的是示例，最好参考项目的实际案例来进行理解和调整
- 这个是最原始的写法，注重简单，第二版是优雅版本（推荐使用）

```python
# in services/calculation.py
def calculate_discount(price: float, user_level: int) -> float:
    if user_level == 1:
        return price * 0.95
    if user_level == 2:
        return price * 0.9
    if price > 1000:
        return price * 0.85
    return price

# in tests/test_unit/test_calculation.py
def test_calculate_discount():
    assert calculate_discount(100, 1) == 95.0
    assert calculate_discount(200, 2) == 180.0
    assert calculate_discount(1200, 0) == 1020
    assert calculate_discount(50, 0) == 50.0
```

> 注意，这里是需要手动去编写调用的参数以及返回的结果的，并且结果推荐人工计算而不是由程序完成
> 每次修改了源码逻辑（比如计算公式），测试文件也要同步的修改

---

```python
import pytest
from services.calculation import calculate_discount

# 数据驱动：左边是输入参数，右边是预期结果
test_data = [
    (100, 1, 95.0),           # 测试等级1
    (200, 2, 180.0),          # 测试等级2
    (1200, 0, 1200 * 0.85),   # 测试大额消费
    (50, 0, 50.0),            # 测试普通消费
]

# 只需要写一次逻辑
@pytest.mark.parametrize("price, user_level, expected", test_data)
def test_calculate_discount_smart(price, user_level, expected):
    # 实际调用
    result = calculate_discount(price, user_level)
    # 断言比对
    assert result == expected
```

- 这是使用 @pytest.mark.parametrize 来把“数据”和“逻辑”分离，在 pytest 框架中常用
- 增删改数据的时候只需要维护 test_data 列表即可，
- 能做到独立报错，即第 2 条数据错了，pytest 会明确告诉你只挂了第 2 条，其他 3 条依然通过
- **注意：测试的共同点就是手动编写调用参数以及返回结果**

## 集成测试

- 这是金字塔中层，测试 API 端点是否正常工作，包括：路由、依赖注入、请求体验证 (Pydantic)、数据库交互、序列化等
- 特点：
  - 真实：它模拟一个真实的 HTTP 请求，并检查响应
  - 覆盖广：一个集成测试可以覆盖从网络请求到数据库查询再返回的整个链路

## 温馨提示与策略

**温馨提示**

- 不应该过多 Mock！Mock 的是无法控制或成本很高的东西
- 最好是第三方 API：支付网关、邮件服务等
- 或者微服务依赖：你的服务需要调用的其他内部服务，这里指的是微服务架构了
- 不要写无效的测试：Pydantic 和 FastAPI 的校验功能已经被其开发者充分测试过了，你还要写额外的测试？

**策略**

- 初学者可能很难断定什么情况下需要写测试，测试的目的是保证基础功能能用，语法无错误，以及修改代码、增加健壮性或者关联其他模块的时候保证其正常
- 这里给出的是我自己的一些策略思想
  1、觉得要测试或者产生了哪怕一丝的犹豫那就测试
  2、使用功能的时候出现了 bug，然后你需要修复，为它添加测试
  3、未来上线的时候遇到 bug，是你没写过的测试并且需要修复，或者你写过但是还是出 bug，请完善这个测试或者补充这个测试

## sqlite 测试

新增了使用 sqlite 内存数据库测试，在开发过程中推荐使用这个测试

项目本身默认使用 sqlite 测试，如果想使用 mysql 只需要更改.env 文件的 test_db_type 的值为 mysql 即可
