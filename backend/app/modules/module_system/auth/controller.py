from typing import Union, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.common.core.dependencies import db_getter, get_current_user
from backend.app.common.core.logger import log
from backend.app.common.response import JSONResponse, SuccessResponse
from backend.app.modules.module_system.auth.schema import JWTOutSchema
from .schema import AuthSchema, LoginSchema, RefreshTokenSchema
from .service import LoginService
from ..user.model import UserModel

AuthRouter = APIRouter(prefix="/auth", tags=["认证管理"])


@AuthRouter.post("/login", summary="用户登录", description="用户登录接口", response_model=JWTOutSchema)
async def login_controller(
        request: Request,
        login_data: LoginSchema,
    db: AsyncSession = Depends(db_getter)
) -> Union[JSONResponse, Dict]:
    """
    用户登录

    参数:
    - login_data (LoginSchema): 登录数据，包含phone/email和password
    - db (AsyncSession): 异步数据库会话

    返回:
    - JSONResponse: 登录响应
    """
    auth = AuthSchema(db=db)
    result = await LoginService.login(request=request,data=login_data, auth=auth)

    log.info(f"用户{login_data.mobile}登录成功")

    return SuccessResponse(data=result.model_dump(),msg="登录成功")


@AuthRouter.post("/logout", summary="用户退出", description="用户退出登录")
async def logout_controller(
    current_user: UserModel = Depends(get_current_user)
) -> JSONResponse:
    """
    用户退出登录

    参数:
    - current_user (UserModel): 当前登录用户（通过JWT解析）

    返回:
    - JSONResponse: 退出成功响应
    """
    log.info(f"用户 {current_user.username} 退出登录")
    return SuccessResponse(msg="退出成功")


@AuthRouter.post("/refresh", summary="刷新令牌", description="使用refresh_token刷新访问令牌", response_model=JWTOutSchema)
async def refresh_token_controller(
    data: RefreshTokenSchema,
    db: AsyncSession = Depends(db_getter)
) -> Union[JSONResponse, Dict]:
    """
    刷新访问令牌

    参数:
    - data (RefreshTokenSchema): 刷新令牌数据
    - db (AsyncSession): 异步数据库会话

    返回:
    - JSONResponse: 新的JWT令牌
    """
    auth = AuthSchema(db=db)
    result = await LoginService.refresh_token_service(data=data, auth=auth)

    return SuccessResponse(data=result.model_dump(), msg="刷新成功")



