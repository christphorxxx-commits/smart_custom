from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .database import async_db_session
from fastapi import Request

async def db_getter() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话连接

    返回:
    - AsyncSession: 数据库会话连接
    """
    async with async_db_session() as session:
        async with session.begin():
            yield session

from fastapi import Depends, HTTPException
from backend.app.common.utils.jwt_util import JwtUtil
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.crud import UserCRUD

async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(db_getter),
):
    """
    获取当前登录用户

    参数:
    - request (Request): 请求对象
    - db (AsyncSession): 数据库会话

    返回:
    - UserModel: 当前登录用户对象

    异常:
    - HTTPException: 认证失败时抛出
    """
    # 从请求头中获取Authorization token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    # 提取token
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    # 解析token
    try:
        payload = JwtUtil.decode_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    # 获取用户UUID
    user_uuid = payload.sub

    # 创建AuthSchema实例
    auth = AuthSchema(db=db)

    # 根据UUID获取用户信息
    user = await UserCRUD(auth).get_by_uuid_crud(user_uuid)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user