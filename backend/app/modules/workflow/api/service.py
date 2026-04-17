from typing import List, Dict, Any, Optional

from bson import ObjectId

from backend.app.common.core.logger import log
from backend.app.common.enums import AgentType
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.api.crud import AppCRUD, AppMongoCRUD
from backend.app.modules.workflow.api.model import App, AiApp
from backend.app.modules.workflow.api.schema import (
    CreateAppSchema, UpdateWorkflowAgentSchema, UpdateChatAgentSchema,
    ChatSystemConfigSchema, AppInfoSchema,
)
from backend.app.common.utils.common_util import uuid4_str

class AppService:
    """应用业务逻辑层"""

    @staticmethod
    async def get_available_apps(auth: AuthSchema) -> List[Dict[str, Any]]:
        """
        获取当前用户可用的应用列表

        参数:
        - auth (AuthSchema): 认证信息

        返回:
        - List[Dict[str, Any]]: 格式化后的应用信息列表
        """
        # 从PG查询可用应用
        app_crud = AppCRUD(auth)
        apps = await app_crud.get_available_apps_for_user_crud(auth.user.id)

        # 使用 AppInfoSchema 序列化后转字典返回
        result = []
        for app in apps:
            schema = AppInfoSchema(
                app_id=app.id,
                uuid=app.uuid,
                name=app.name,
                description=app.description,
                icon=app.icon,
                type= app.type,
                is_public=app.is_public,
            )
            result.append(schema.model_dump())

        return result

    @staticmethod
    async def get_default_app(auth: AuthSchema) -> Optional[App]:
        """
        获取默认应用

        参数:
        - auth (AuthSchema): 认证信息

        返回:
        - Optional[App]: 默认应用MongoDB文档，不存在返回None
        """
        app_id = "8488bff8-30a2-415d-8d1d-7c4fb4b6567b"
        app_mongo_crud = AppMongoCRUD()
        default_app = await app_mongo_crud.get_app_by_appid_crud(app_id)

        return default_app

    @staticmethod
    async def get_app_by_object_id(objectid: ObjectId) -> Optional[App]:
        """
        根据ObjectId获取应用

        参数:
        - objectid (ObjectId): MongoDB文档ID

        返回:
        - Optional[App]: 应用MongoDB文档，不存在返回None
        """
        app_mongo_crud = AppMongoCRUD()
        default_app = await app_mongo_crud.get_by_id(objectid)

        return default_app

    @staticmethod
    async def get_app_by_app_id(app_id: str) -> Dict[str, Any]:
        """
        根据app_id获取应用

        参数:
        - uuid (str): 应用UUID

        返回:
        - Optional[App]: 应用MongoDB文档，不存在返回None
        """
        app_mongo_crud = AppMongoCRUD()
        app = await app_mongo_crud.get_app_by_appid_crud(app_id)
        app.type = str(app.type)

        app.created_at = app.created_at.isoformat()
        app.updated_at = app.updated_at.isoformat()


        return app.model_dump()

    # @staticmethod
    # async def save_app(
    #     auth: AuthSchema,
    #     user: UserModel,
    #     data: CreateAppSchema
    # ) -> Dict[str, Any]:
    #     """
    #     保存新建的工作流应用
    #
    #     先创建基本信息到 PostgreSQL，再创建完整配置到 MongoDB
    #
    #     参数:
    #     - auth (AuthSchema): 认证信息
    #     - user (UserModel): 当前用户
    #     - data (CreateAppSchema): 创建请求数据
    #
    #     返回:
    #     - Dict[str, Any]: 创建结果
    #     """
    #
    #     # 生成全局唯一 uuid，用于跨库关联
    #     uuid_val = uuid4_str()
    #     user_id_str = str(user.id)
    #
    #     # 格式转换：双重保险，确保存储的一定是正确格式
    #     def convert_node(node: dict) -> dict:
    #         node_type_map = {
    #             "input": "start",
    #             "output": "end",
    #             "if": "router",
    #             "llm": "llm",
    #             "retrieve": "retrieve",
    #         }
    #         original_type = node.get("type", "")
    #         backend_type = node_type_map.get(original_type, original_type)
    #         return {
    #             "id": node.get("id", ""),
    #             "type": backend_type,
    #             "config": node.get("data", {}).get("config", {}) or node.get("config", {})
    #         }
    #
    #     def convert_edge(edge: dict) -> dict:
    #         source = edge.get("source") or edge.get("sourceNodeId", "")
    #         target = edge.get("target") or edge.get("targetNodeId", "")
    #         return {
    #             "source": source,
    #             "target": target,
    #             "type": edge.get("type", "normal"),
    #             "condition": edge.get("condition", None)
    #         }
    #
    #     converted_nodes = [convert_node(n) for n in data.nodes]
    #     converted_edges = [convert_edge(e) for e in data.edges]
    #
    #     # 1. 创建到 PostgreSQL（存储基本信息）
    #     app_crud = AppCRUD(auth)
    #     data.uuid = uuid_val
    #     data.user_id = user.id
    #
    #     pg_app = await app_crud.create_app_pg_crud(data=data)
    #     log.info(f"[{user.username}] 成功保存应用到PG: {data.name}")
    #
    #     # 2. 创建完整配置到 MongoDB（存储转换后的nodes和edges）
    #     app_mongo_crud = AppMongoCRUD()
    #     mongo_app = await app_mongo_crud.create_mongo_app_crud(data=data)
    #     log.info(f"[{user.username}] 成功保存应用到MongoDB: {data.name}, id={str(mongo_app.id)}")
    #
    #     return {
    #         "uuid": uuid_val,
    #         "mongo_id": str(mongo_app.id),
    #         "message": "保存成功"
    #     }

    @staticmethod
    async def update_app(
        auth: AuthSchema,
        user: UserModel,
        data: UpdateWorkflowAgentSchema | UpdateChatAgentSchema,
    ) -> Dict[str, Any]:
        """
        更新工作流应用

        参数:
        - auth: 认证信息
        - user: 当前用户
        - uuid: PostgreSQL主键ID
        - data: 更新数据

        返回:
        - Dict: 更新结果
        """
        # 1. 从PG获取应用基本信息
        app_crud = AppCRUD(auth)
        pg_app = await app_crud.get_app_by_id_crud(data.id)
        if not pg_app:
            return {"success": False, "message": "应用不存在"}

        # 检查权限：只有创建者可以更新
        if pg_app.user_id != user.id:
            return {"success": False, "message": "无权限更新此应用"}

        # 2. 更新PG基本信息
        pg_app.name = data.name
        pg_app.description = data.description
        pg_app.icon = data.icon
        pg_app.is_public = data.is_public

        await app_crud.update_app_pg_crud(data)

        # 3. 更新MongoDB完整配置
        app_mongo_crud = AppMongoCRUD()
        mongo_app = await app_mongo_crud.get_app_by_appid_crud(pg_app.uuid)
        if not mongo_app:
            return {"success": False, "message": "应用配置不存在"}

        # 4. 格式转换并构建Mongo更新数据
        mongo_app.name = data.name
        mongo_app.description = data.description
        mongo_app.icon = data.icon
        mongo_app.is_public = data.is_public

        # 如果提供了nodes和edges，转换格式后更新
        if data.nodes is not None or data.edges is not None:
            # 格式转换：双重保险，确保存储的一定是正确格式
            def convert_node(node: dict) -> dict:
                node_type_map = {
                    "input": "start",
                    "output": "end",
                    "if": "router",
                    "llm": "llm",
                    "retrieve": "retrieve",
                }
                original_type = node.get("type", "")
                backend_type = node_type_map.get(original_type, original_type)
                return {
                    "id": node.get("id", ""),
                    "type": backend_type,
                    "config": node.get("data", {}).get("config", {}) or node.get("config", {})
                }

            def convert_edge(edge: dict) -> dict:
                source = edge.get("source") or edge.get("sourceNodeId", "")
                target = edge.get("target") or edge.get("targetNodeId", "")
                return {
                    "source": source,
                    "target": target,
                    "type": edge.get("type", "normal"),
                    "condition": edge.get("condition", None)
                }

            if data.nodes is not None:
                converted_nodes = [convert_node(n) for n in data.nodes]
                mongo_app.nodes = converted_nodes

            if data.edges is not None:
                converted_edges = [convert_edge(e) for e in data.edges]
                mongo_app.edges = converted_edges

        # 5. 执行MongoDB更新
        await app_mongo_crud.update_mongo_app_crud(mongo_app.id, data)

        log.info(f"[{user.username}] 成功更新Agent应用: id={pg_app.id}, type={pg_app.type}")

        return {
            "id": pg_app.id,
            "uuid": pg_app.uuid,
            "message": "更新成功"
        }

    @staticmethod
    async def create_app(
        auth: AuthSchema,
        user: UserModel,
        data: CreateAppSchema,
    ) -> Dict[str, Any]:
        """
        创建新应用（生命周期第一步）
        - 先创建基本信息到 PostgreSQL 和 MongoDB
        - 客户端获取 id/uuid 后进入画布编辑
        - 编辑完成后调用 update 更新节点配置

        参数:
        - auth: 认证信息
        - user: 当前用户
        - data: 创建数据，包含基础信息 + 初始nodes/edges（可以为空）

        返回:
        - Dict: 创建结果，包含 id/uuid
        """
        # 生成全局唯一 uuid，用于跨库关联
        # 1. 创建到 PostgreSQL（存储基本信息）
        app_crud = AppCRUD(auth)
        data.uuid = uuid4_str()
        data.user_id = user.id

        pg_app = await app_crud.create_app_pg_crud(data=data)
        log.info(f"[{user.username}] 创建新应用到PG: {data.name}, type={data.type}")

        # 3. 创建到 MongoDB（存储初始nodes和edges）
        app_mongo_crud = AppMongoCRUD()

        mongo_app = await app_mongo_crud.create_mongo_app_crud(data=data)
        log.info(f"[{user.username}] 创建新应用到MongoDB: {data.name}, id={str(mongo_app.id)}, type={pg_app.type}")

        return {
            "app_id": pg_app.id,
            "uuid": pg_app.uuid,
            "mongo_id": str(mongo_app.id),
            "message": "创建成功"
        }





