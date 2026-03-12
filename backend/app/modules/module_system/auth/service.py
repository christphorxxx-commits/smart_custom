from datetime import datetime,timedelta

from backend.app.config.setting import settings
from backend.app.modules.module_system.auth.schema import LoginSchema, AuthSchema, JWTOutSchema, JWTPlayloadSchema
from backend.app.modules.module_system.user.crud import UserCRUD
from backend.app.common.core.logger import log
from fastapi import HTTPException,Request
from backend.app.common.response import JSONResponse, SuccessResponse
from backend.app.common.utils.hash_bcrpy_util import PwdUtil
from backend.app.common.core.exceptions import CustomException
from backend.app.modules.module_system.user.model import UserModel
from backend.app.common.utils.jwt_util import JwtUtil


class LoginService:
    """登录认证服务"""
    @classmethod
    async def login(cls, data: LoginSchema, auth: AuthSchema) -> JWTOutSchema:

        user_crud = UserCRUD(auth)

        #传入的用户信息
        current_mobile = data.phone
        current_password = data.password

        if not current_password:
            raise CustomException(msg="密码不能为空")


        #获取数据库中用户
        user = await user_crud.get_by_mobile_crud(current_mobile)

        #如果不用户存在
        if not user:
            raise CustomException(msg="用户不存在")

        #验证密码
        if not PwdUtil.verify(current_password, user.password):
            raise CustomException(msg="密码错误")

        token = await cls.create_token_service(user)

        return token

    @classmethod
    async def create_token_service(cls, user: UserModel)-> JWTOutSchema:

        #用户唯一id
        user_uuid = user.uuid
        user_name = user.name
        #记录用户信息
        log.info(f"用户ID：{user.id}，用户名：{user_name}正在创建JWT令牌")

        now = datetime.utcnow()

        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
        refresh_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        access_token =JwtUtil.create_access_token(playload=JWTPlayloadSchema(
            sub=user_uuid,
            is_refresh=False,
            exp=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME),
        ))

        refresh_token = JwtUtil.create_access_token(playload=JWTPlayloadSchema(
            sub=user_uuid,
            is_refresh=True,
            exp=now + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        ))

        return JWTOutSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expires.total_seconds()),
            token_type=settings.TOKEN_TYPE,
        )



