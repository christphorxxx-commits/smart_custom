from pydantic import BaseModel
from typing import TypeVar, Sequence, Generic, Dict, Any, List, Optional, Type, Union
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result
from sqlalchemy import asc, func, select, delete, Select, desc, update
from sqlalchemy import inspect as sa_inspect

from backend.app.common.core.base_model import MappedBase
from backend.app.common.core.exceptions import CustomException

from backend.app.modules.module_system.auth.schema import AuthSchema

ModelType = TypeVar("ModelType", bound=MappedBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
OutSchemaType = TypeVar("OutSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础数据层"""

    def __init__(self,model: Type[ModelType], auth: AuthSchema):
        """
                初始化CRUDBase类

                参数:
                - model (Type[ModelType]): 数据模型类。
                - auth (AuthSchema): 认证信息。

                返回:
                - None
                """
        self.model = model
        self.auth = auth

    async def create(self, data: Union[CreateSchemaType, Dict]) -> ModelType:
        """
        创建新对象

        参数:
        - data (Union[CreateSchemaType, Dict]): 对象属性

        返回:
        - ModelType: 新创建的对象实例

        异常:
        - CustomException: 创建失败时抛出异常
        """
        try:
            obj_dict = data if isinstance(data, dict) else data.model_dump()
            obj = self.model(**obj_dict)

            # 设置字段值（只检查一次current_user）
            if self.auth.user:
                if hasattr(obj, "created_id"):
                    setattr(obj, "created_id", self.auth.user.id)
                if hasattr(obj, "updated_id"):
                    setattr(obj, "updated_id", self.auth.user.id)

            self.auth.db.add(obj)
            await self.auth.db.flush()
            await self.auth.db.refresh(obj)
            return obj
        except Exception as e:
            raise CustomException(msg=f"创建失败: {str(e)}")