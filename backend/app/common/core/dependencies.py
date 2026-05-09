from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from .database import async_db_session, mongo_db_session
from fastapi import Request, WebSocket
from fastapi import Depends, HTTPException
from backend.app.common.utils.jwt_util import JwtUtil
from backend.app.common.utils.token_blacklist import token_blacklist
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.crud import UserCRUD
from .exceptions import CustomException


async def db_getter() -> AsyncGenerator[AsyncSession, None]:
    """获取SQL数据库会话连接

    返回:
    - AsyncSession: SQL数据库会话连接
    """
    async with async_db_session() as session:
        async with session.begin():
            yield session


def mongo_getter() -> AsyncIOMotorDatabase:
    """获取MongoDB数据库连接（依赖注入使用）

    返回:
    - AsyncIOMotorDatabase: MongoDB默认数据库连接
    说明:
    - 如果MongoDB未配置，会抛出 ValueError
    - 在需要MongoDB的路由中使用: `db: AsyncIOMotorDatabase = Depends(mongo_getter)`
    """
    if mongo_db_session is None:
        raise ValueError("MongoDB未配置或连接失败，请检查环境变量 MONGO_URI 和 MONGO_DB")
    return mongo_db_session





async def _get_user_by_token(token: str, db: AsyncSession):
    """
    根据token获取用户信息（内部复用函数）

    参数:
    - token: JWT token字符串
    - db: 数据库会话

    返回:
    - UserModel: 用户对象

    异常:
    - CustomException: token无效或用户不存在
    """
    # 检查token是否在黑名单中
    if token_blacklist.is_blacklisted(token):
        raise CustomException(status_code=401, msg="凭证已失效，请重新登录")

    try:
        payload = JwtUtil.decode_token(token)
    except Exception as e:
        raise CustomException(status_code=401, msg=f"非法凭证，{str(e)}")

    user_uuid = payload.sub
    auth = AuthSchema(db=db)
    user = await UserCRUD(auth).get_by_uuid_crud(user_uuid)

    if not user:
        raise CustomException(status_code=401, msg="用户不存在")

    return user


async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(db_getter),
):
    """
    获取当前登录用户（HTTP请求）

    参数:
    - request (Request): 请求对象
    - db (AsyncSession): SQL数据库会话

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

    return await _get_user_by_token(token, db)


async def get_ws_current_user(
        websocket: WebSocket,
        token: Optional[str] = None,
        db: AsyncSession = Depends(db_getter),
):
    """
    获取WebSocket当前登录用户

    参数:
    - websocket: WebSocket连接对象
    - token: JWT token（从query参数传递）
    - db: SQL数据库会话

    返回:
    - UserModel | None: 用户对象，验证失败返回None
    """
    if not token:
        # 尝试从headers中获取
        auth_header = websocket.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    if not token:
        return None

    try:
        return await _get_user_by_token(token, db)
    except Exception:
        return None


async def extract_token_from_request(request: Request) -> Optional[str]:
    """
    从HTTP请求中提取token

    参数:
    - request: 请求对象

    返回:
    - str | None: token字符串，提取失败返回None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    return auth_header.split(" ")[1] if " " in auth_header else auth_header