from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.common.core.dependencies import db_getter
from backend.app.common.response import JSONResponse, SuccessResponse
from backend.app.common.core.logger import log
from backend.app.common.utils.hash_bcrpy_util import PwdUtil
from backend.app.common.utils.jwt_util import JwtUtil
from ..user.model import UserModel
from ..user.crud import UserCRUD
from .schema import AuthSchema

AuthRouter = APIRouter(prefix="/auth", tags=["认证管理"])


@AuthRouter.post("/login", summary="用户登录", description="用户登录接口")
async def login_controller(
    login_data: dict,
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    """
    用户登录

    参数:
    - login_data (dict): 登录数据，包含phone/email和password
    - db (AsyncSession): 异步数据库会话

    返回:
    - JSONResponse: 登录响应
    """
    try:
        # 提取登录参数
        phone = login_data.get("phone")
        email = login_data.get("email")
        password = login_data.get("password")

        if not password:
            raise HTTPException(status_code=400, detail="密码不能为空")

        # 根据phone或email查询用户
        user_crud = UserCRUD(AuthSchema(db=db))
        if phone:
            user = await user_crud.get_by_mobile_crud(mobile=phone)
        elif email:
            user = await user_crud.get_by_email_crud(email=email)
        else:
            raise HTTPException(status_code=400, detail="请提供手机号或邮箱")

        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        if user.status != "0":
            raise HTTPException(status_code=403, detail="用户账号已被禁用")

        # 验证密码
        if not PwdUtil.verify(password, user.password):
            raise HTTPException(status_code=401, detail="密码错误")

        # 生成token
        token = JwtUtil.create_access_token(user_id=user.id, username=user.username)

        # 更新最后登录时间
        await user_crud.update_last_login_crud(user_id=user.id)

        log.info(f"用户 {user.username} 登录成功")

        # 构建返回数据
        user_data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "mobile": user.mobile,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login
        }

        return SuccessResponse(
            data={
                "token": token,
                "user": user_data
            },
            msg="登录成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"登录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="登录失败，请稍后重试")
