from typing import Union, Dict

from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.common.core.dependencies import db_getter
from backend.app.common.response import JSONResponse, SuccessResponse
from backend.app.common.core.logger import log
from backend.app.common.utils.hash_bcrpy_util import PwdUtil
from backend.app.common.utils.jwt_util import JwtUtil
from backend.app.modules.module_system.auth.schema import JWTOutSchema
from .service import LoginService
from ..user.model import UserModel
from ..user.crud import UserCRUD
from .schema import AuthSchema, LoginSchema

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


