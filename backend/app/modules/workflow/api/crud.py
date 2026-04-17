from typing import List, Optional, Dict, Any

from bson import ObjectId
from sqlalchemy import select

from backend.app.common.core.base_crud import CRUDBase
from backend.app.common.core.base_mongo_crud import BaseMongoCRUD
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.workflow.api.model import App, AiApp
from backend.app.modules.workflow.api.schema import (
    CreateAppSchema, UpdateWorkflowAgentSchema, UpdateChatAgentSchema,
)


class AppCRUD(CRUDBase[AiApp, CreateAppSchema, UpdateChatAgentSchema | UpdateWorkflowAgentSchema]):
    """
    应用数据访问层 (PostgreSQL)

    负责操作 PostgreSQL 的 AiApp 表，存储应用基本信息和权限控制
    """

    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化应用CRUD

        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=AiApp, auth=auth)

    async def get_available_apps_for_user_crud(
            self,
            current_user_id: int,
    ) -> List[AiApp]:
        """
        获取当前用户可用的应用列表（PostgreSQL查询）

        参数:
        - current_user_id (int): 当前用户ID

        返回:
        - List[AiApp]: 可用应用列表
        权限规则：用户自己创建的 OR 公开应用，且状态为启用
        """
        stmt = select(AiApp).where(
            (AiApp.user_id == current_user_id) | (AiApp.is_public == True)
        ).where(
            AiApp.status == '0'  # 只返回启用的应用
        ).order_by(AiApp.created_time.desc())

        result = await self.auth.db.execute(stmt)
        apps = result.scalars().all()
        return list(apps)

    async def create_app_pg_crud(
            self,
            data: CreateAppSchema
    ) -> AiApp:
        """
        创建应用基本信息到 PostgreSQL

        参数:
        - uuid (int): 用户ID
        - name (str): 应用名称
        - uuid (str): 应用UUID
        - description (Optional[str]): 应用描述
        - icon (Optional[str]): 图标emoji
        - is_public (bool): 是否公开
        - type (str): 应用类型

        返回:
        - AiApp: 创建后的 PG 记录
        """

        return await self.create(data)

    async def update_app_pg_crud(
            self,
            data: UpdateWorkflowAgentSchema
    ) -> AiApp:
        """
        更新应用基本信息到 PostgreSQL

        参数:
        - app (AiApp): 现有PG应用记录
        - update_data (Dict[str, Any]): 更新数据字典

        返回:
        - AiApp: 更新后的 PG 记录
        """
        return await self.update(id=data.id, data=data)

    async def get_app_by_id_crud(self, id: int) -> Optional[AiApp]:
        """
        根据PG主键ID获取应用基本信息

        参数:
        - uuid (int): 应用PostgreSQL主键ID

        返回:
        - Optional[AiApp]: PG应用记录，不存在返回None
        """
        stmt = select(AiApp).where(AiApp.id == id)
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_app_by_app_id_crud(self, app_id: str) -> Optional[AiApp]:
        """
        根据app_id (UUID)获取应用基本信息

        参数:
        - app_id (str): 应用UUID

        返回:
        - Optional[AiApp]: PG应用记录，不存在返回None
        """
        stmt = select(AiApp).where(AiApp.uuid == app_id)
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()


class AppMongoCRUD(BaseMongoCRUD[App, CreateAppSchema, UpdateWorkflowAgentSchema | UpdateChatAgentSchema]):
    """
    工作流应用数据访问层 (MongoDB)

    负责操作 MongoDB 的 App 文档，存储完整工作流配置（nodes, edges）
    """

    def __init__(self):
        """
        初始化MongoDB CRUD
        """
        super().__init__(model=App)

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

        return await self.create(data.model_dump())

    async def update_mongo_app_crud(
            self,
            doc_id: ObjectId,
            data: UpdateWorkflowAgentSchema | UpdateChatAgentSchema,
    ) -> None:
        """
        更新MongoDB应用文档

        参数:
        - doc_id (ObjectId): MongoDB文档ID
        - update_data (Dict[str, Any]): 更新数据
        """
        await self.update(doc_id, str(data.user_id), data)

    async def get_app_by_appid_crud(self, app_id: str) -> Optional[App]:
        """
        根据app_id从MongoDB获取完整应用配置

        参数:
        - uuid (str): 应用UUID

        返回:
        - Optional[App]: MongoDB中的应用文档，不存在返回None
        """
        return await self.get_by_field("uuid", app_id)
