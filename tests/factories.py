from typing import TypeVar, Generic
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.persistence import AsyncPersistenceProtocol
from polyfactory import Use
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, DesignUnit

fake = Faker("zh_CN")
T = TypeVar("T")

# =============================================================================
# 通用配置
# =============================================================================


class AsyncSQLAlchemyPersistence(AsyncPersistenceProtocol[T]):
    """
    异步持久化处理器
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, data: T) -> T:
        self.session.add(data)
        await self.session.flush()
        await self.session.refresh(data)
        return data

    async def save_many(self, data: list[T]) -> list[T]:
        self.session.add_all(data)
        await self.session.flush()
        for item in data:
            await self.session.refresh(item)
        return data


class BaseFactory(SQLAlchemyFactory[T], Generic[T]):

    __is_base_factory__ = True
    __set_relationships__ = False

    @classmethod
    async def create_async(cls, session: AsyncSession, **kwargs) -> T:
        """
        重写 create_async
        1. 拦截 session 参数
        2. 初始化持久化处理器
        3. 保存数据
        """
        # 在内存中构建对象
        data = cls.build(**kwargs)

        # 初始化持久化工具
        persistence = AsyncSQLAlchemyPersistence(session=session)

        # 保存并返回
        return await persistence.save(data)


# =============================================================================
# 业务逻辑配置
# =============================================================================


class UserFactory(BaseFactory[User]):
    __model__ = User

    name = Use(fake.name)
    password = Use(lambda: "test_password_123")
    # 模拟加密后的密码
    password_hash = Use(
        lambda: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqGfZJQv9u"
    )


class DesignUnitFactory(BaseFactory[DesignUnit]):
    __model__ = DesignUnit

    contact = Use(fake.name)
    tel = Use(fake.phone_number)
    email = Use(fake.email)
    address = Use(lambda: f"{fake.city()}{fake.street_address()}")
