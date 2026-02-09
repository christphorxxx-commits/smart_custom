# -*- coding: utf-8 -*-

from typing import Sequence, Any
from datetime import datetime

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

