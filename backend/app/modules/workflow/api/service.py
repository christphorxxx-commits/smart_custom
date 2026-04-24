import json
from typing import List, Dict, Any, Optional, Coroutine
from collections.abc import AsyncIterable
from bson import ObjectId
from fastapi.sse import ServerSentEvent

from backend.app.common.core.logger import log
from backend.app.common.utils.common_util import uuid4_str
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.api.crud import AppCRUD, AppMongoCRUD
from backend.app.modules.workflow.api.model import AiAppModel
from backend.app.modules.workflow.api.schema import (
    CreateAppSchema, UpdateAgentSchema, AppInfoSchema, BaseCreateAppSchema,
)
from backend.app.modules.workflow.app import App


class AppService:
    """应用业务逻辑层"""
    # 内存缓存已编译的应用 {uuid: App}
    app_storage: Dict[str, App] = {}

    @staticmethod
    def register_app(app: App) -> str:
        """注册一个app到缓存，返回uuid"""
        AppService.app_storage[app.uuid] = app
        return app.uuid

    @staticmethod
    async def exist(auth: AuthSchema, uuid: str) -> App | None:
        """
        从缓存获取 App，如果缓存不存在则从 MongoDB 加载并编译
        - uuid: 应用 UUID
        - returns: 编译好的 App 实例，不存在返回 None
        """
        if uuid in AppService.app_storage:
            return AppService.app_storage[uuid]

        # 从 MongoDB 根据 app_id 获取完整配置
        app_mongo_crud = AppMongoCRUD(auth)
        mongo_app = await app_mongo_crud.get_app_by_uuid_crud(uuid)
        if not mongo_app:
            return None

        # 前端格式已经统一，直接使用 MongoDB 中保存的原始数据（包含 x y 坐标）
        # 不需要格式转换，nodes 已经是正确格式：id/type/x/y/config
        app_data = {
            "name": mongo_app.name,
            "description": mongo_app.description,
            "uuid": mongo_app.uuid,
            "nodes": mongo_app.nodes,
            "edges": mongo_app.edges,
        }
        app = App(**app_data)
        AppService.register_app(app)
        return app

    @staticmethod
    async def chat_sse(app: App, query: ChatQuerySchema) -> AsyncIterable[ServerSentEvent]:
        """
        SSE 流式对话生成器
        Yields each token event as it's generated
        """
        # 是否是第一个token，用于去掉开头的markdown标题符号
        is_first = True
        async for event in app.astream_tokens({"input": query.message}):
            if event["type"] == "token":
                data = event["token"]
                # 去掉开头的 markdown 标题符号 ## 等
                if is_first:
                    # 去掉开头连续的 # 和空格
                    data = data.lstrip('# ')
                    is_first = False
                # 如果data为空，跳过不输出
                if data:
                    yield ServerSentEvent(data=data, event="token")

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
                type=app.type,
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
        app_mongo_crud = AppMongoCRUD(auth)
        default_app = await app_mongo_crud.get_app_by_uuid_crud(app_id)

        return default_app

    @staticmethod
    async def get_app_by_object_id(auth: AuthSchema, objectid: ObjectId) -> Optional[App]:
        """
        根据ObjectId获取应用

        参数:
        - objectid (ObjectId): MongoDB文档ID

        返回:
        - Optional[App]: 应用MongoDB文档，不存在返回None
        """
        app_mongo_crud = AppMongoCRUD(auth)
        default_app = await app_mongo_crud.get_by_id(objectid)

        return default_app

    @staticmethod
    async def get_app_by_uuid(auth: AuthSchema, uuid: str) -> Dict[str, Any]:
        """
        根据app_id获取应用

        参数:
        - uuid (str): 应用UUID

        返回:
        - Optional[App]: 应用MongoDB文档，不存在返回None
        """
        app_mongo_crud = AppMongoCRUD(auth)
        app = await app_mongo_crud.get_app_by_uuid_crud(uuid)
        app.type = str(app.type)

        app.created_at = app.created_at.isoformat()
        app.updated_at = app.updated_at.isoformat()
        app.id=str(app.id)

        return app.model_dump()

    @staticmethod
    async def update_app(
            auth: AuthSchema,
            user: UserModel,
            data: UpdateAgentSchema,
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
        # 1. 从PG获取应用基本信息（通过 uuid 查询）
        app_crud = AppCRUD(auth)
        pg_app = await app_crud.get_app_by_uuid_crud(data.uuid)
        if not pg_app:
            return {"success": False, "message": "应用不存在"}

        # 检查权限：只有创建者可以更新
        if pg_app.user_id != user.id:
            return {"success": False, "message": "无权限更新此应用"}

        # 2. 更新PG基本信息
        update_data = BaseCreateAppSchema(
            name=data.name,
            icon=data.icon,
            is_public=data.is_public,
            description=data.description
        )
        await app_crud.update_app_pg_crud(pg_app.id, update_data)
        f"[{user.username}] PG成功更新Agent应用: id={pg_app.id}, type={pg_app.type}"

        # 3. 更新MongoDB完整配置
        app_mongo_crud = AppMongoCRUD(auth)
        mongo_app = await app_mongo_crud.get_app_by_uuid_crud(pg_app.uuid)
        if not mongo_app:
            return {"success": False, "message": "应用配置不存在"}

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
        app_crud = AppCRUD(auth=auth)
        data.uuid = uuid4_str()
        data.user_id = auth.user.id  # PG 需要 int，外键引用 sys_user.id 必须是 int
        data.type = data.type.value
        pg_app = await app_crud.create_app_pg_crud(data=data)
        log.info(f"[{auth.user.username}] 创建新应用到PG: {data.name}, type={data.type}")

        # 2. 如果是对话式Agent (CHAT)，自动生成默认nodes和edges
        from backend.app.common.enums import AgentType
        if data.type == AgentType.CHAT.value:
            # 对话式Agent默认生成线性工作流
            # 默认: start → llm → end
            # 启用知识库: start → retrieve → llm → end
            enable_kb = getattr(data, 'enableKnowledgeBase', False)
            if enable_kb:
                data.nodes = [
                    {"id": "start", "type": "start", "x": 100, "y": 200, "config": {}},
                    {"id": "retrieve", "type": "retrieve", "x": 300, "y": 200, "config": {
                        "collection_name": "knowledge_base",
                        "top_k": 5,
                        "score_threshold": 0.5
                    }},
                    {"id": "llm", "type": "llm", "x": 500, "y": 200, "config": {
                        "model": "qwen-max",
                        "systemPrompt": "你是一个智能AI助手，请基于上下文回答用户问题{question}",
                        "temperature": 0.7,
                        "maxTokens": 5000
                    }},
                    {"id": "end", "type": "end", "x": 700, "y": 200, "config": {}}
                ]
                data.edges = [
                    {"source": "start", "target": "retrieve", "type": "normal", "condition": None},
                    {"source": "retrieve", "target": "llm", "type": "normal", "condition": None},
                    {"source": "llm", "target": "end", "type": "normal", "condition": None}
                ]
            else:
                data.nodes = [
                    {"id": "start", "type": "start", "x": 100, "y": 200, "config": {}},
                    {"id": "llm", "type": "llm", "x": 350, "y": 200, "config": {
                        "model": "qwen-max",
                        "systemPrompt": "你是一个智能AI助手",
                        "temperature": 0.7,
                        "maxTokens": 5000
                    }},
                    {"id": "end", "type": "end", "x": 600, "y": 200, "config": {}}
                ]
                data.edges = [
                    {"source": "start", "target": "llm", "type": "normal", "condition": None},
                    {"source": "llm", "target": "end", "type": "normal", "condition": None}
                ]

        # 3. 创建到 MongoDB（存储初始nodes和edges）
        app_mongo_crud = AppMongoCRUD(auth=auth)
        # MongoDB App 模型需要 user_id 是 str（约定存储字符串形式 ID）
        # 复制一份 data 转换 user_id 到 string
        data.user_id = str(auth.user.id)

        mongo_app = await app_mongo_crud.create_mongo_app_crud(data=data)
        log.info(f"[{auth.user.username}] 创建新应用到MongoDB: {data.name}, id={str(mongo_app.id)}, type={pg_app.type}")

        return {
            "app_id": pg_app.id,
            "uuid": pg_app.uuid,
            "mongo_id": str(mongo_app.id),
            "message": "创建成功"
        }

    @staticmethod
    async def get_pg_app_by_uuid(
            uuid:str,
            auth: AuthSchema,
    )-> Coroutine[Any, Any, AiAppModel | None]:
        app_crud = AppCRUD(auth)
        return app_crud.get_app_by_uuid_crud(uuid)

    @staticmethod
    async def get_app_detail(auth, uuid) -> Dict[str, Any]:
        # 先从 PostgreSQL 根据 uuid 找到 PG 记录，获取 PG 主键 id
        app_crud = AppCRUD(auth)
        pg_app = await app_crud.get_app_by_uuid_crud(uuid)

        if not pg_app:
            return {"success": False, "message": "应用不存在"}

        # 检查权限：只有创建者可以更新
        if pg_app.user_id != auth.user.id:
            return {"success": False, "message": "无权查看该app"}

        # 从MongoDB直接获取完整配置
        mongo_app = await AppService.get_app_by_uuid(auth,uuid)
        # 添加 pg_id 到返回数据，供前端更新请求使用
        mongo_app['pg_id'] = pg_app.id
        return mongo_app


