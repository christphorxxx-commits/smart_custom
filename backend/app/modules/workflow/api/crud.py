from typing import List, Optional, Dict, Any

from sqlalchemy import select

from backend.app.common.core.base_crud import CRUDBase
from backend.app.common.core.base_mongo_crud import BaseMongoCRUD
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.workflow.api.model import App, AiApp
from backend.app.modules.workflow.api.schema import CreateAppSchema, UpdateAppSchema


class AppCRUD(CRUDBase[AiApp, CreateAppSchema, UpdateAppSchema]):
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
        user_id: int,
        name: str,
        app_id: str,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        is_public: bool = False,
    ) -> AiApp:
        """
        创建应用基本信息到 PostgreSQL

        参数:
        - user_id (int): 用户ID
        - name (str): 应用名称
        - app_id (str): 应用UUID
        - description (Optional[str]): 应用描述
        - icon (Optional[str]): 图标emoji
        - is_public (bool): 是否公开

        返回:
        - AiApp: 创建后的 PG 记录
        """
        pg_data = {
            "name": name,
            "app_id": app_id,
            "user_id": user_id,
            "description": description,
            "icon": icon,
            "is_public": is_public,
            "type": "workflow",
        }
        return await self.create(pg_data)

    async def get_app_by_id_crud(self, app_id: int) -> Optional[AiApp]:
        """
        根据PG主键ID获取应用基本信息

        参数:
        - app_id (int): 应用PostgreSQL主键ID

        返回:
        - Optional[AiApp]: PG应用记录，不存在返回None
        """
        stmt = select(AiApp).where(AiApp.id == app_id)
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()

class AppMongoCRUD(BaseMongoCRUD[App]):
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
        user_id: str,
        name: str,
        description: Optional[str],
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        app_id: Optional[str] = None,
        icon: Optional[str] = None,
        is_public: bool = False,
    ) -> App:
        """
        创建一个新的工作流应用到MongoDB

        参数:
        - user_id (str): 创建用户ID
        - name (str): 工作流名称
        - description (Optional[str]): 工作流描述
        - nodes (List[Dict[str, Any]]): 节点列表
        - edges (List[Dict[str, Any]]): 边列表
        - app_id (Optional[str]): 应用UUID
        - icon (Optional[str]): 图标emoji
        - is_public (bool): 是否公开

        返回:
        - App: 创建好的WorkflowApp对象
        """
        data = {
            "app_id": app_id,
            "name": name,
            "description": description,
            "user_id": user_id,
            "nodes": nodes,
            "edges": edges,
            "icon": icon,
            "is_public": is_public,
            "created_by": user_id,
            "updated_by": user_id,
        }
        return await self.create(data)

    async def get_app_by_appid_crud(self, app_id: str) -> Optional[App]:
        """
        根据app_id从MongoDB获取完整应用配置

        参数:
        - app_id (str): 应用UUID

        返回:
        - Optional[App]: MongoDB中的应用文档，不存在返回None
        """
        return await self.get_by_field("app_id", app_id)
