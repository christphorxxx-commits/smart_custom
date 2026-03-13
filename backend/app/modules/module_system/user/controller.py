from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.common.core.dependencies import db_getter
from backend.app.common.response import StreamingResponse,JSONResponse,SuccessResponse
from backend.app.common.core.logger import log
from .schema import UserRegisterSchema
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

