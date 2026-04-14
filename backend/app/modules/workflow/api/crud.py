from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pydantic import Field
from sqlalchemy import select

from backend.app.common.core.logger import log
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.workflow.api.model import App, AiApp


class AppCRUD:
    """工作流应用数据访问层"""



    @staticmethod
    async def get_app_by_appid(app_id:str):
        return App.find({"app_id": app_id})

    @staticmethod
    async def create_app(
        user_id: str,
        name: str,
        description: Optional[str],
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        app_id: Optional[str] = Field(default=None, alias="id"),
        icon: Optional[str] = None,
        is_public: bool = False,
    ) -> App:
        """创建一个新的工作流应用

        返回: 创建好的WorkflowApp对象，其中.id字段就是自动生成的ObjectId
              可以通过str(app.id)获取字符串格式的id
        """
        app = App(
            app_id=app_id,
            name=name,
            description=description,
            user_id=user_id,
            nodes=nodes,
            edges=edges,
            icon=icon,
            is_public=is_public,
            created_by=user_id,
            updated_by=user_id,
        )
        await app.insert()
        # ✅ 创建完成后，app.id 已经自动赋值了！就是MongoDB自动生成的_id
        return app

    @staticmethod
    async def get_by_id(workflow_id: str | ObjectId) -> Optional[App]:
        """根据ID获取工作流"""
        if isinstance(workflow_id, str):
            workflow_id = ObjectId(workflow_id)

        try:
            app = await App.get(workflow_id)
            if app and not app.is_deleted:
                return app
            return None
        except Exception:
            return None

    @staticmethod
    async def list_user_workflows(
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[App]:
        """获取用户创建的所有工作流（分页）"""
        apps = await App.find(
            {"user_id": user_id, "is_deleted": False}
        ).sort([("updated_at", -1)]).skip(skip).limit(limit).to_list()
        return apps

    @staticmethod
    async def count_user_workflows(user_id: str) -> int:
        """统计用户工作流总数"""
        count = await App.find(
            {"user_id": user_id, "is_deleted": False}
        ).count()
        return count

    @staticmethod
    async def update_workflow(
        workflow_id: str | ObjectId,
        user_id: str,
        **kwargs
    ) -> Optional[App]:
        """更新工作流信息"""
        app = await AppCRUD.get_by_id(workflow_id)
        if not app:
            return None

        # 检查权限
        if str(app.user_id) != str(user_id):
            return None

        # 更新传入的字段
        for key, value in kwargs.items():
            if hasattr(app, key):
                setattr(app, key, value)

        app.updated_at = datetime.utcnow()
        app.updated_by = user_id
        app.version += 1
        await app.save()
        return app

    @staticmethod
    async def delete_workflow(workflow_id: str | ObjectId, user_id: str) -> tuple[bool, str]:
        """软删除工作流"""
        try:
            app = await AppCRUD.get_by_id(workflow_id)
            if not app:
                return False, "工作流不存在"
            if app.is_deleted:
                return False, "工作流已删除"
            if str(app.user_id) != str(user_id):
                return False, "无权限删除此工作流"

            app.is_deleted = True
            app.updated_at = datetime.utcnow()
            app.updated_by = user_id
            await app.save()
            return True, "删除成功"
        except Exception as e:
            log.error(f"删除工作流出错: {e}", exc_info=True)
            return False, str(e)

    @staticmethod
    async def list_public_apps(
        skip: int = 0,
        limit: int = 20
    ) -> List[App]:
        """获取公开的工作流列表"""
        apps = await App.find(
            {"is_public": True, "is_deleted": False}
        ).sort([("updated_at", -1)]).skip(skip).limit(limit).to_list()
        return apps

    @staticmethod
    async def get_available_apps_for_user(
        auth: AuthSchema,
        current_user_id: int,
    ) -> List[AiApp]:
        """获取当前用户可用的应用列表（PostgreSQL查询）
        权限规则：用户自己创建的 OR 公开应用，且状态为启用
        """
        stmt = select(AiApp).where(
            (AiApp.user_id == current_user_id) | (AiApp.is_public == True)
        ).where(
            AiApp.status == '0'  # 只返回启用的应用
        ).order_by(AiApp.created_time.desc())

        result = await auth.db.execute(stmt)
        apps = result.scalars().all()
        return list(apps)

    @staticmethod
    async def get_app_by_appid(
        app_id: str,
    ) -> Optional[App]:
        """根据app_id从MongoDB获取完整应用配置"""
        app = await App.find_one(
            {"app_id": app_id, "is_deleted": False}
        )
        return app
