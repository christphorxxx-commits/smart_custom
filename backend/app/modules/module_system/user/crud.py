# -*- coding: utf-8 -*-

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.common.core.base_crud import CRUDBase
from backend.app.modules.module_system.auth.schema import AuthSchema
from .model import UserModel
from .schema import UserCreateSchema, UserUpdateSchema


class UserCRUD(CRUDBase[UserModel, UserCreateSchema, UserUpdateSchema]):
    """用户模块数据层"""



    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化用户CRUD

        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=UserModel, auth=auth)

    async def get_by_mobile_crud(self, mobile: str) -> UserModel | None:
        """
        根据手机号查询用户

        参数:
        - mobile (str): 手机号

        返回:
        - UserModel | None: 用户对象或None
        """

        stmt = (
            select(self.model)
                .options(
                selectinload(UserModel.created_by),
                selectinload(UserModel.created_by)
            )
            .where(self.model.mobile == mobile)
        )
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_crud(self, email: EmailStr) -> UserModel | None:
        """
        根据邮箱查询用户

        参数:
        - email (str): 邮箱

        返回:
        - UserModel | None: 用户对象或None
        """
        from sqlalchemy import select
        stmt = (select(self.model)
                .options(
                selectinload(UserModel.created_by),
                selectinload(UserModel.created_by)
            )
            .where(self.model.email == email)
        )
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_login_crud(self, user_id: int) -> bool:
        """
        更新用户最后登录时间

        参数:
        - uuid (int): 用户ID

        返回:
        - bool: 更新是否成功
        """
        from sqlalchemy import update
        from datetime import datetime
        
        stmt = update(self.model).where(self.model.id == user_id).values(last_login=datetime.utcnow())
        result = await self.auth.db.execute(stmt)
        await self.auth.db.commit()
        return result.rowcount > 0

    async def get_by_uuid_crud(self, uuid: str) -> UserModel | None:
        """
        根据UUID查询用户 (兼容: uuid -> uuid)

        参数:
        - uuid (str): 用户UUID

        返回:
        - UserModel | None: 用户对象或None
        """
        from sqlalchemy import select
        stmt = (select(self.model).where(self.model.user_id == uuid)
        .options(
            selectinload(self.model.created_by),
            selectinload(self.model.updated_by)
        ))
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()

    # async def get_by_username_crud(self, username: str) -> UserModel | None:
    #     """
    #     根据用户名查询用户
    #
    #     :param
    #     - username: 用户名
    #
    #     :return:
    #     """

