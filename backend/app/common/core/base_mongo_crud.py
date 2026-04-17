from typing import TypeVar, Generic, Optional, Type, List, Any, Union
from pydantic import BaseModel
from bson import ObjectId

from beanie import SortDirection

from backend.app.common.core.base_model import BaseMongoDocument

# 类型变量
ModelType = TypeVar("ModelType", bound=BaseMongoDocument)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
OutSchemaType = TypeVar("OutSchemaType", bound=BaseModel)

class BaseMongoCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    MongoDB Beanie ODM 基础数据访问层基类

    封装通用的增删改查操作，所有 MongoDB 文档的 CRUD 类都应该继承此类
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化 MongoDB CRUD

        参数:
        - model (Type[ModelType]): Beanie 文档模型类
        """
        self.model = model

    async def get_by_id(self, doc_id: str | ObjectId) -> Optional[ModelType]:
        """
        根据 ID 获取文档（过滤已软删除）

        参数:
        - doc_id (str | ObjectId): 文档 ID

        返回:
        - Optional[ModelType]: 文档对象，不存在或已删除返回 None
        """
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)

        try:
            doc = await self.model.get(doc_id)
            if doc and not doc.is_deleted:
                return doc
            return None
        except Exception:
            return None

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """
        根据单个字段查询单个文档（过滤已软删除）

        参数:
        - field_name (str): 字段名
        - value (any): 字段值

        返回:
        - Optional[ModelType]: 文档对象，不存在返回 None
        """
        query = {
            field_name: value,
            "is_deleted": False
        }
        return await self.model.find_one(query)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        sort_dir: SortDirection = SortDirection.DESCENDING
    ) -> List[ModelType]:
        """
        获取所有未删除文档（分页）

        参数:
        - skip (int): 跳过条数
        - limit (int): 返回条数
        - order_by (str): 排序字段
        - sort_dir (SortDirection): 排序方向

        返回:
        - List[ModelType]: 文档列表
        """
        docs = await self.model.find(
            {"is_deleted": False}
        ).sort([(order_by, sort_dir)]).skip(skip).limit(limit).to_list()
        return docs

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "updated_at",
        sort_dir: SortDirection = SortDirection.ASCENDING
    ) -> List[ModelType]:
        """
        获取指定用户创建的所有未删除文档（分页）

        参数:
        - uuid (str): 用户 ID
        - skip (int): 跳过条数
        - limit (int): 返回条数
        - order_by (str): 排序字段
        - sort_dir (SortDirection): 排序方向

        返回:
        - List[ModelType]: 文档列表
        """
        docs = await self.model.find(
            {"uuid": user_id, "is_deleted": False}
        ).sort([(order_by, sort_dir)]).skip(skip).limit(limit).to_list()
        return docs

    async def count_all(self) -> int:
        """
        统计所有未删除文档总数

        返回:
        - int: 文档总数
        """
        count = await self.model.find(
            {"is_deleted": False}
        ).count()
        return count

    async def count_by_user(self, user_id: str) -> int:
        """
        统计指定用户创建的未删除文档总数

        参数:
        - uuid (str): 用户 ID

        返回:
        - int: 文档总数
        """
        count = await self.model.find(
            {"uuid": user_id, "is_deleted": False}
        ).count()
        return count

    async def create(self, data: Union[CreateSchemaType, dict]) -> ModelType:
        """
        创建新文档

        参数:
        - data (dict): 文档数据

        返回:
        - ModelType: 创建后的文档对象
        """
        doc = self.model(**data)
        await doc.insert()
        return doc

    async def update(
        self,
        id: str | ObjectId,
        user_id: str,
        data: Union[UpdateSchemaType, dict]
    ) -> Optional[ModelType]:
        """
        更新文档（检查用户权限）

        参数:
        - doc_id (str | ObjectId): 文档 ID
        - uuid (str): 当前用户 ID（权限检查）
        - update_data (dict): 需要更新的字段

        返回:
        - Optional[ModelType]: 更新后的文档，权限不足或不存在返回 None
        """
        from datetime import datetime

        doc = await self.get_by_id(id)
        if not doc:
            return None

        # 检查权限
        if hasattr(doc, "uuid") and str(doc.user_id) != str(user_id):
            return None

        # 更新传入字段
        for key, value in data.items():
            if hasattr(doc, key):
                setattr(doc, key, value)

        # 更新时间和更新人
        doc.updated_at = datetime.utcnow()
        if hasattr(doc, "updated_by"):
            doc.updated_by = user_id

        # 增加版本号
        if hasattr(doc, "version"):
            doc.version += 1

        await doc.save()
        return doc

    async def delete(
        self,
        id: str | ObjectId,
        user_id: str
    ) -> tuple[bool, str]:
        """
        软删除文档（检查用户权限）

        参数:
        - doc_id (str | ObjectId): 文档 ID
        - uuid (str): 当前用户 ID（权限检查）

        返回:
        - tuple[bool, str]: (是否成功, 消息)
        """
        from datetime import datetime

        doc = await self.get_by_id(id)
        if not doc:
            return False, "文档不存在"
        if doc.is_deleted:
            return False, "文档已删除"

        # 检查权限
        if hasattr(doc, "uuid") and str(doc.user_id) != str(user_id):
            return False, "无权限删除此文档"

        doc.is_deleted = True
        doc.updated_at = datetime.utcnow()
        if hasattr(doc, "updated_by"):
            doc.updated_by = user_id

        await doc.save()
        return True, "删除成功"
