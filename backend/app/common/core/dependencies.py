from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .database import async_db_session

async def db_getter() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话连接

    返回:
    - AsyncSession: 数据库会话连接
    """
    async with async_db_session() as session:
        async with session.begin():
            yield session