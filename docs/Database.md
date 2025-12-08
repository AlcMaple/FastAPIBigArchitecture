# 2 Database

fastapi 依赖注入中，通常有两种数据库操作的方式：手动 commit 或者 依赖中自动处理事务

本框架采用的是自动处理事务的方式，它能够减少代码冗余，不容易出错，维护简单，也是 fastapi官方较为推荐的方式

主要位于 db/database.py 文件中

```python
async def get_async_session() -> AsyncSession:
    """获取异步数据库会话(查询)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_async_session_with_transaction() -> AsyncGenerator[AsyncSession, None]:
    """获取自动事务管理的异步数据库会话（增删改）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 自动提交事务
            await session.commit()
        except Exception:
            # 自动回滚
            await session.rollback()
            raise
        finally:
            await session.close()
```

这里提供了两种方式针对不同的增删改查场景获取数据库会话，其中 get_async_session() 用于查询场景，get_async_session_with_transaction() 用于增删改场景。

get_async_session() 直接返回一个异步会话，可以直接使用，不需要手动关闭会话，适用于不需要手动 commit 的事务

get_async_session_with_transaction() 返回一个异步会话，并且在使用完毕后自动提交事务，如果出现异常，则自动回滚事务，并抛出异常

出现异常自动回滚事务有个好处，可以保证数据库的一致性，避免数据丢失，但是需要注意的是需要保持一个请求一个事务的原则

这里的一个请求一个事务并不是说一个请求只能操作数据库一次，意思是你一个请求的所有过程都在一个事务中，你当中涉及的所有数据库的操作都必须包裹在这一个事务当中

也可以理解为你完成了所有的数据库操作后，再 commit 事务，防止前半段 commit 后，如果后半段出现异常，回滚无法覆盖到前半段的 commit 操作

举个例子就是网上购物下单：

你点击“下单”按钮，后端服务器收到了一个创建订单的请求。这个请求需要做好几件事：

操作1：在 orders 表里创建一条新的订单记录。

操作2：从 products 表里减少对应商品的库存。

操作3：在 payments 表里记录一笔待支付的款项。

操作4：可能还会在 user_activity_log 表里记录用户的下单行为。

这 4 个数据库操作是一个整体。不会发生“订单创建了，但库存没减少”或者“库存减少了，但订单创建失败”的情况。

“一个请求一个事务”机制保证了：

如果一切顺利：当这 4 个操作都成功执行后，在请求的最后，事务被 commit（提交），所有更改永久生效。

如果中途出错：比如在第 2 步扣减库存时，发现库存不足，代码抛出异常。那么整个事务就会被 rollback（回滚），之前已经执行的第 1 步（创建订单）也会被自动撤销。数据库会回到接收这个请求之前的状态，就好像什么都没发生过一样，保证了数据的完整性和一致性。