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

    async def update(self, id: int, data: Union[UpdateSchemaType, Dict]) -> ModelType:
        """
        更新对象

        参数:
        - id (int): 对象ID
        - data (Union[UpdateSchemaType, Dict]): 更新的属性及值

        返回:
        - ModelType: 更新后的对象实例

        异常:
        - CustomException: 更新失败时抛出异常
        """
        try:
            obj_dict = data if isinstance(data, dict) else data.model_dump(exclude_unset=True, exclude={"id"})
            obj = await self.get(id=id)
            if not obj:
                raise CustomException(msg="更新对象不存在")

            # 设置字段值（只检查一次current_user）
            if self.auth.user:
                if hasattr(obj, "updated_id"):
                    setattr(obj, "updated_id", self.auth.user.id)

            for key, value in obj_dict.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            await self.auth.db.flush()
            await self.auth.db.refresh(obj)

            # 权限二次确认：flush后再次验证对象仍在权限范围内
            # 防止并发修改导致的权限逃逸（如其他事务修改了created_id）
            verify_obj = await self.get(id=id)
            if not verify_obj:
                # 对象已被删除或权限已失效
                raise CustomException(msg="更新失败，对象不存在或无权限访问")

            return obj
        except Exception as e:
            raise CustomException(msg=f"更新失败: {str(e)}")

    async def delete(self, ids: List[int]) -> None:
        """
        删除对象

        参数:
        - ids (List[int]): 对象ID列表

        异常:
        - CustomException: 删除失败时抛出异常
        """
        try:
            # 先查询确认权限,避免删除无权限的数据
            objs = await self.list(search={"id": ("in", ids)})
            accessible_ids = [obj.id for obj in objs]

            # 检查是否所有ID都有权限访问
            inaccessible_count = len(ids) - len(accessible_ids)
            if inaccessible_count > 0:
                raise CustomException(msg=f"无权限删除{inaccessible_count}条数据")

            if not accessible_ids:
                return  # 没有可删除的数据

            mapper = sa_inspect(self.model)
            pk_cols = list(getattr(mapper, "primary_key", []))
            if not pk_cols:
                raise CustomException(msg="模型缺少主键，无法删除")
            if len(pk_cols) > 1:
                raise CustomException(msg="暂不支持复合主键的批量删除")

            # 只删除有权限的数据
            sql = delete(self.model).where(pk_cols[0].in_(accessible_ids))
            await self.auth.db.execute(sql)
            await self.auth.db.flush()
        except Exception as e:
            raise CustomException(msg=f"删除失败: {str(e)}")

    async def clear(self) -> None:
        """
        清空对象表

        异常:
        - CustomException: 清空失败时抛出异常
        """
        try:
            sql = delete(self.model)
            await self.auth.db.execute(sql)
            await self.auth.db.flush()
        except Exception as e:
            raise CustomException(msg=f"清空失败: {str(e)}")

    async def set(self, ids: List[int], **kwargs) -> None:
        """
        批量更新对象

        参数:
        - ids (List[int]): 对象ID列表
        - **kwargs: 更新的属性及值

        异常:
        - CustomException: 更新失败时抛出异常
        """
        try:
            # 先查询确认权限,避免更新无权限的数据
            objs = await self.list(search={"id": ("in", ids)})
            accessible_ids = [obj.id for obj in objs]

            # 检查是否所有ID都有权限访问
            inaccessible_count = len(ids) - len(accessible_ids)
            if inaccessible_count > 0:
                raise CustomException(msg=f"无权限更新{inaccessible_count}条数据")

            if not accessible_ids:
                return  # 没有可更新的数据

            mapper = sa_inspect(self.model)
            pk_cols = list(getattr(mapper, "primary_key", []))
            if not pk_cols:
                raise CustomException(msg="模型缺少主键，无法更新")
            if len(pk_cols) > 1:
                raise CustomException(msg="暂不支持复合主键的批量更新")

            # 只更新有权限的数据
            sql = update(self.model).where(pk_cols[0].in_(accessible_ids)).values(**kwargs)
            await self.auth.db.execute(sql)
            await self.auth.db.flush()
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"批量更新失败: {str(e)}")

    async def __build_conditions(self, **kwargs) -> List[ColumnElement]:
        """
        构建查询条件

        参数:
        - **kwargs: 查询参数

        返回:
        - List[ColumnElement]: SQL条件表达式列表

        异常:
        - CustomException: 查询参数不存在时抛出异常
        """
        conditions = []
        for key, value in kwargs.items():
            if value is None or value == "":
                continue

            attr = getattr(self.model, key)
            if isinstance(value, tuple):
                seq, val = value
                if seq == "None":
                    conditions.append(attr.is_(None))
                elif seq == "not None":
                    conditions.append(attr.isnot(None))
                elif seq == "date" and val:
                    conditions.append(func.date_format(attr, "%Y-%m-%d") == val)
                elif seq == "month" and val:
                    conditions.append(func.date_format(attr, "%Y-%m") == val)
                elif seq == "like" and val:
                    conditions.append(attr.like(f"%{val}%"))
                elif seq == "in" and val:
                    conditions.append(attr.in_(val))
                elif seq == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                    conditions.append(attr.between(val[0], val[1]))
                elif seq == "!=" and val:
                    conditions.append(attr != val)
                elif seq == ">" and val:
                    conditions.append(attr > val)
                elif seq == ">=" and val:
                    conditions.append(attr >= val)
                elif seq == "<" and val:
                    conditions.append(attr < val)
                elif seq == "<=" and val:
                    conditions.append(attr <= val)
                elif seq == "==" and val:
                    conditions.append(attr == val)
            else:
                conditions.append(attr == value)
        return conditions

    def __order_by(self, order_by: List[Dict[str, str]]) -> List[ColumnElement]:
        """
        获取排序字段

        参数:
        - order_by (List[Dict[str, str]]): 排序字段列表,格式为 [{'id': 'asc'}, {'name': 'desc'}]

        返回:
        - List[ColumnElement]: 排序字段列表

        异常:
        - CustomException: 排序字段不存在时抛出异常
        """
        columns = []
        for order in order_by:
            for field, direction in order.items():
                column = getattr(self.model, field)
                columns.append(desc(column) if direction.lower() == 'desc' else asc(column))
        return columns

    def __loader_options(self, preload: Optional[List[Union[str, Any]]] = None) -> List[Any]:
        """
        构建预加载选项

        参数:
        - preload (Optional[List[Union[str, Any]]]): 预加载关系，支持关系名字符串或SQLAlchemy loader option

        返回:
        - List[Any]: 预加载选项列表
        """
        options = []
        # 获取模型定义的默认加载选项
        model_loader_options = getattr(self.model, '__loader_options__', [])

        # 合并所有需要预加载的选项
        all_preloads = set(model_loader_options)
        if preload:
            for opt in preload:
                if isinstance(opt, str):
                    all_preloads.add(opt)
        elif preload == []:
            # 如果明确指定空列表，则不使用任何预加载
            all_preloads = set()

        # 处理所有预加载选项
        for opt in all_preloads:
            if isinstance(opt, str):
                # 使用selectinload来避免在异步环境中的MissingGreenlet错误
                if hasattr(self.model, opt):
                    options.append(selectinload(getattr(self.model, opt)))
            else:
                # 直接使用非字符串的加载选项
                options.append(opt)

        return options