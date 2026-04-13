from typing import List, Dict, Any

from backend.app.modules.module_system.auth.schema import AuthSchema
from .crud import AppCRUD


class AppService:
    """应用业务逻辑层"""

    @staticmethod
    async def get_available_apps(auth: AuthSchema) -> List[Dict[str, Any]]:
        """获取当前用户可用的应用列表
        返回: 格式化后的应用信息列表
        """
        # 从PG查询可用应用
        apps = await AppCRUD.get_available_apps_for_user(auth, auth.user.id)

        # 转换为字典返回
        result = []
        for app in apps:
            result.append({
                "id": app.id,
                "app_id": app.app_id,
                "name": app.name,
                "description": app.description,
                "icon": app.icon,
                "type": app.type,
                "is_public": app.is_public,
            })

        return result
