from typing import List, Optional

from bson import ObjectId
from sqlalchemy import select

from backend.app.common.core.base_crud import CRUDBase
from backend.app.common.core.base_mongo_crud import BaseMongoCRUD
from backend.app.common.core.logger import log
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.workflow.api.model import App, AiAppModel
from backend.app.modules.workflow.api.schema import (
    CreateAppPGSchema, CreateAppSchema, UpdateAgentSchema, BaseCreateAppSchema,
)


class AppCRUD(CRUDBase[AiAppModel, CreateAppSchema, UpdateAgentSchema]):
    """
    应用数据访问层 (PostgreSQL)

    负责操作 PostgreSQL 的 AiAppModel 表，存储应用基本信息和权限控制
    """

    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化应用CRUD

        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=AiAppModel, auth=auth)

    async def get_available_apps_for_user_crud(
            self,
            current_user_id: int,
    ) -> List[AiAppModel]:
        """
        获取当前用户可用的应用列表（PostgreSQL查询）

        参数:
        - current_user_id (int): 当前用户ID

        返回:
        - List[AiAppModel]: 可用应用列表
        权限规则：用户自己创建的 OR 公开应用，且状态为启用
        """
        stmt = select(AiAppModel).where(
            (AiAppModel.user_id == current_user_id) | (AiAppModel.is_public == True)
        ).where(
            AiAppModel.status == '0'  # 只返回启用的应用
        ).order_by(AiAppModel.created_time.desc())

        result = await self.auth.db.execute(stmt)
        apps = result.scalars().all()
        return list(apps)

    async def create_app_pg_crud(
            self,
            data: CreateAppPGSchema
    ) -> AiAppModel:
        """
        创建应用基本信息到 PostgreSQL

        参数:
        - data (CreateAppPGSchema): 创建数据，只包含 PG 需要的基本字段

        返回:
        - AiAppModel: 创建后的 PG 记录
        """
        # PostgreSQL AiAppModel 只存储基本信息，不存储系统配置（系统配置在MongoDB）
        # CreateAppPGSchema 只包含 PG 需要的字段，直接序列化

        pg_data = data.model_dump(exclude_unset=True)

        return await self.create(pg_data)
    async def update_app_pg_crud(
            self,
            app_id: int,
            data: BaseCreateAppSchema
    ) -> AiAppModel:
        """
        更新应用基本信息到 PostgreSQL

        参数:
        - app_id: PG 主键 id
        - data: 更新数据，只提取 PG 需要的字段

        返回:
        - AiAppModel: 更新后的 PG 记录
        """
        # PostgreSQL AiAppModel 只更新基本信息，系统配置只更新 MongoDB
        # 只提取需要更新的字段，避免 user_id=None 覆盖原有非空值

        return await self.update(id=app_id, data=data.model_dump())

    async def get_app_by_id_crud(self, id: int) -> Optional[AiAppModel]:
        """
        根据PG主键ID获取应用基本信息（公开接口）

        参数:
        - id (int): 应用PostgreSQL主键ID

        返回:
        - Optional[AiAppModel]: PG应用记录，不存在返回None
        """
        return await self.get(id)

    async def get_app_by_uuid_crud(self, uuid: str) -> Optional[AiAppModel]:
        """
        根据app_id (UUID)获取应用基本信息

        参数:
        - app_id (str): 应用UUID

        返回:
        - Optional[AiAppModel]: PG应用记录，不存在返回None
        """

        stmt = select(AiAppModel).where(AiAppModel.uuid == uuid)
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()


class AppMongoCRUD(BaseMongoCRUD[App, CreateAppSchema, UpdateAgentSchema]):
    """
    工作流应用数据访问层 (MongoDB)

    负责操作 MongoDB 的 App 文档，存储完整工作流配置（nodes, edges）
    """

    def __init__(self,auth: AuthSchema):
        """
        初始化MongoDB CRUD
        """
        self.auth = auth
        super().__init__(model=App,auth=auth)

    async def create_mongo_app_crud(
            self,
            data: CreateAppSchema,
    ) -> App:
        """
        创建一个新的工作流应用到MongoDB

        参数:
        - uuid (str): 创建用户ID
        - name (str): 工作流名称
        - description (Optional[str]): 工作流描述
        - nodes (List[Dict[str, Any]]): 节点列表
        - edges (List[Dict[str, Any]]): 边列表
        - uuid (Optional[str]): 应用UUID
        - icon (Optional[str]): 图标emoji
        - is_public (bool): 是否公开
        - type (str): 应用类型
        - config (Optional[Dict[str, Any]]): 对话式Agent顶层配置

        返回:
        - App: 创建好的WorkflowApp对象
        """

        return await self.create(data.model_dump(exclude_unset=True))

    async def update_mongo_app_crud(
            self,
            doc_id: ObjectId,
            data: UpdateAgentSchema,
    ) -> App:
        """
        更新MongoDB应用文档

        参数:
        - doc_id (ObjectId): MongoDB文档ID
        - update_data (Dict[str, Any]): 更新数据
        """
        log.info(f"更新{doc_id}数据")
        return await self.update(doc_id, data)

    async def get_app_by_uuid_crud(self, uuid: str) -> Optional[App]:
        """
        根据app_id从MongoDB获取完整应用配置

        参数:
        - uuid (str): 应用UUID

        返回:
        - Optional[App]: MongoDB中的应用文档，不存在返回None
        """
        return await self.get_by_field("uuid", uuid)
