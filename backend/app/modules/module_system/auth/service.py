from datetime import datetime, timedelta

from fastapi import Request

from backend.app.common.core.exceptions import CustomException
from backend.app.common.core.logger import log
from backend.app.common.utils.hash_bcrpy_util import PwdUtil
from backend.app.common.utils.jwt_util import JwtUtil
from backend.app.config.setting import settings
from backend.app.modules.module_system.auth.schema import LoginSchema, AuthSchema, JWTOutSchema, JWTPlayloadSchema
from backend.app.modules.module_system.auth.schema import RefreshTokenSchema
from backend.app.modules.module_system.user.crud import UserCRUD
from backend.app.modules.module_system.user.model import UserModel


class LoginService:
    """登录认证服务"""
    @classmethod
    async def login(cls, request: Request,data: LoginSchema, auth: AuthSchema) -> JWTOutSchema:

        user_crud = UserCRUD(auth)

        #传入的用户信息
        current_mobile = data.mobile
        current_email = data.email
        current_password = data.password

        if not current_password:
            raise CustomException(msg="密码不能为空")

        #获取数据库中用户 - 支持手机号或邮箱登录
        user = None
        if current_mobile:
            user = await user_crud.get_by_mobile_crud(current_mobile)
        elif current_email:
            user = await user_crud.get_by_email_crud(current_email)
        else:
            raise CustomException(msg="手机号或邮箱不能为空")

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
        user_uuid = user.user_id
        user_name = user.name
        #记录用户信息
        log.info(f"用户ID：{user.id}，用户名：{user_name}正在创建JWT令牌")

        now = datetime.utcnow()

        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
        refresh_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        access_token =JwtUtil.create_access_token(payload=JWTPlayloadSchema(
            sub=user_uuid,
            is_refresh=False,
            exp=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_TIME),
        ))

        refresh_token = JwtUtil.create_access_token(payload=JWTPlayloadSchema(
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

    @classmethod
    async def refresh_token_service(cls, data: RefreshTokenSchema, auth: AuthSchema) -> JWTOutSchema:
        """
        刷新访问令牌

        参数:
        - data (RefreshTokenSchema): 刷新令牌数据
        - auth (AuthSchema): 认证信息模型

        返回:
        - JWTOutSchema: 新的JWT令牌
        """
        # 解析刷新token
        payload = JwtUtil.decode_token(data.refresh_token)

        # 检查是否是刷新token
        if not payload.is_refresh:
            raise CustomException(msg="无效的刷新token", code=10401, status_code=401)

        # 获取用户UUID
        user_uuid = payload.sub

        # 根据UUID获取用户信息
        user = await UserCRUD(auth).get_by_uuid_crud(user_uuid)
        if not user:
            raise CustomException(msg="用户不存在", code=10401, status_code=401)

        # 生成新token
        token = await cls.create_token_service(user)

        log.info(f"用户 {user.username} 刷新token成功")

        return token



