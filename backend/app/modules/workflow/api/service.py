from typing import List, Dict, Any, Optional

from bson import ObjectId

from backend.app.common.core.logger import log
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.api.crud import AppCRUD, AppMongoCRUD
from backend.app.modules.workflow.api.model import App
from backend.app.modules.workflow.api.schema import AppInfoSchema, CreateAppSchema
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
                id=app.id,
                app_id=app.app_id,
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
    async def get_app_by_app_id(app_id: str) -> Optional[App]:
        """
        根据app_id获取应用

        参数:
        - app_id (str): 应用UUID

        返回:
        - Optional[App]: 应用MongoDB文档，不存在返回None
        """
        app_mongo_crud = AppMongoCRUD()
        default_app = await app_mongo_crud.get_app_by_appid_crud(app_id)

        return default_app

    @staticmethod
    async def save_app(
        auth: AuthSchema,
        user: UserModel,
        data: CreateAppSchema
    ) -> Dict[str, Any]:
        """
        保存新建的工作流应用

        先创建基本信息到 PostgreSQL，再创建完整配置到 MongoDB

        参数:
        - auth (AuthSchema): 认证信息
        - user (UserModel): 当前用户
        - data (CreateAppSchema): 创建请求数据

        返回:
        - Dict[str, Any]: 创建结果
        """

        # 生成全局唯一 app_id，用于跨库关联
        app_id = uuid4_str()
        user_id_str = str(user.id)

        # 1. 创建到 PostgreSQL（存储基本信息）
        app_crud = AppCRUD(auth)
        await app_crud.create_app_pg_crud(
            user_id=user.id,
            name=data.name,
            app_id=app_id,
            description=data.description,
            icon=data.icon,
            is_public=data.is_public,
        )
        log.info(f"[{user.username}] 成功保存应用到PG: {data.name}")

        # 2. 创建完整配置到 MongoDB（存储nodes和edges）
        app_mongo_crud = AppMongoCRUD()
        mongo_app = await app_mongo_crud.create_mongo_app_crud(
            user_id=user_id_str,
            name=data.name,
            description=data.description,
            nodes=data.nodes,
            edges=data.edges,
            app_id=app_id,
            icon=data.icon,
            is_public=data.is_public,
        )
        log.info(f"[{user.username}] 成功保存应用到MongoDB: {data.name}, id={str(mongo_app.id)}")

        return {
            "app_id": app_id,
            "mongo_id": str(mongo_app.id),
            "message": "保存成功"
        }
