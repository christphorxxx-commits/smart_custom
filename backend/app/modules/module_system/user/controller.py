from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.common.core.dependencies import db_getter, get_current_user
from backend.app.common.core.logger import log
from backend.app.common.response import JSONResponse, SuccessResponse
from .model import UserModel
from .schema import UserRegisterSchema, UserOutSchema, ChangePasswordSchema
from .service import UserService
from ..auth.schema import AuthSchema

UserRouter = APIRouter(prefix="/user",tags=["用户管理"])

@UserRouter.post("/register",summary="注册用户",description="用户注册")
async def register_user_controller(
    data: UserRegisterSchema,
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    """
    注册用户

    参数:
    - data (UserRegisterSchema): 用户注册模型
    - db (AsyncSession): 异步数据库会话

    返回:
    - JSONResponse: 注册用户JSON响应
    """
    auth = AuthSchema(db=db)
    user_register_result = await UserService.register_user_service(data=data,auth=auth)
    log.info(f"{data.username} 注册用户成功: {user_register_result}")
    return SuccessResponse(data=user_register_result, msg='注册用户成功')


@UserRouter.get("/info", summary="获取当前用户信息", description="获取当前登录用户的信息")
async def get_current_user_info_controller(
    current_user: UserModel = Depends(get_current_user)
) -> JSONResponse:
    """
    获取当前用户信息

    参数:
    - current_user (UserModel): 当前登录用户（通过JWT解析）

    返回:
    - JSONResponse: 当前用户信息
    """
    user_info = UserOutSchema.model_validate(current_user).model_dump()
    return SuccessResponse(data=user_info, msg='获取成功')


@UserRouter.post("/password", summary="修改密码", description="修改当前用户密码")
async def change_password_controller(
    data: ChangePasswordSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    """
    修改当前用户密码

    参数:
    - data (ChangePasswordSchema): 修改密码数据
    - current_user (UserModel): 当前登录用户
    - db (AsyncSession): 异步数据库会话

    返回:
    - JSONResponse: 修改结果
    """
    auth = AuthSchema(db=db)
    result = await UserService.change_password_service(auth=auth, user=current_user, data=data)
    return SuccessResponse(msg=result["message"])

