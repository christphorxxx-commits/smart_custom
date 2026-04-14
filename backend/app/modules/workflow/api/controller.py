import json
from typing import Dict

from bson import ObjectId
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.response import SuccessResponse, ErrorResponse
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.api.model import App
from backend.app.modules.workflow.app import App
from backend.app.modules.workflow.api.crud import AppCRUD
from backend.app.modules.workflow.api.service import AppService
from backend.app.modules.workflow.api.schema import AppResponseSchema

# 内存存储已创建的Workflow应用 {app_id: App}
workflow_storage: Dict[str, App] = {}

AppRouter = APIRouter(prefix="/app", tags=["App"])


def register_workflow(app: App) -> str:
    """注册一个workflow到存储，返回app_id"""
    if not app.app_id:
        from backend.app.common.utils.common_util import uuid4_str
        app.app_id = uuid4_str()
    workflow_storage[app.app_id] = app
    return app.app_id
from pathlib import Path
from backend.app.common.response import StreamResponse

@AppRouter.post("/chat/{app_id}")
async def create_chat(
        app_id: str,
        query: ChatQuerySchema,
) -> StreamResponse:
    """
    HTTP流式运行workflow
    - app_id: workflow应用ID（路径参数）
    - query: 请求body，包含message
    - 返回: 流式token输出，每个chunk是一个token片段
    """
    # 从存储获取已注册的app，如果找不到默认用default.json（方便测试）
    if app_id not in workflow_storage:
        default_json_path = Path(__file__).parent / "default.json"
        with open(default_json_path, "r", encoding="utf-8") as f:
            workflow_data = json.load(f)
        app = App.model_validate(workflow_data)
        app_id = register_workflow(app)
    else:
        app = workflow_storage[app_id]

    # 使用异步迭代，逐token输出，真正的流式响应（SSE格式）
    async def generate():
        async for event in app.astream_tokens({"input": query.message}):
            if event["type"] == "token":
                # SSE 格式：data: "token"\n\n - 使用JSON编码避免引号问题
                data = json.dumps(event["token"], ensure_ascii=False)
                yield f"data: {data}\n\n".encode('utf-8')

    return StreamResponse(generate(), media_type="text/event-stream; charset=utf-8")

@AppRouter.get("/list", summary="获取当前用户可用的应用列表")
async def list_apps(
    current_user: UserModel = Depends(get_current_user),
    db : AsyncSession = Depends(db_getter),
) -> JSONResponse:
    """
    获取当前用户有权限可以使用的所有应用

    权限规则：
    - 用户自己创建的所有应用（不管是否公开）
    - 所有其他用户创建的公开应用
    """

    auth = AuthSchema(db=db,user=current_user)

    data = await AppService.get_available_apps(auth)
    return SuccessResponse(
        data=data,
        msg="获取成功"
    )

@AppRouter.get("/my/list", summary="获取当前用户的所有工作流")
async def list_my_workflows(
    skip: int = 0,
    limit: int = 20,
    current_user: UserModel = Depends(get_current_user)
) -> JSONResponse:
    """获取当前用户创建的所有工作流列表"""
    apps = await AppCRUD.list_user_workflows(str(current_user.id), skip, limit)
    total = await AppCRUD.count_user_workflows(str(current_user.id))
    data = [
        {
            "id": str(app.id),
            "app_id": app.app_id,
            "name": app.name,
            "description": app.description,
            "icon": app.icon,
            "is_public": app.is_public,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
            "version": app.version,
            "nodes": app.nodes,
            "edges": app.edges,
        }
        for app in apps
    ]
    return SuccessResponse(
        data={
            "list": data,
            "total": total,
        },
        msg="获取成功"
    )

@AppRouter.get("/default", summary="获取默认示例工作流")
async def get_default_workflow(
        db: AsyncSession = Depends(db_getter),
) -> JSONResponse:
    """获取默认示例工作流配置，用于编辑器"加载默认"按钮"""
    # from pathlib import Path
    # default_json_path = Path(__file__).parent.parent / "default.json"
    # with open(default_json_path, "r", encoding="utf-8") as f:
    #     default_data = json.load(f)
    auth = AuthSchema(db=db)
    object_id = ObjectId("69dca6647d321630360ce492")
    default_app = await AppService.get_app_by_object_id(object_id)

    # Use schema for serialization
    if not default_app:
        return ErrorResponse(msg="默认应用不存在")

    schema = AppResponseSchema(
        id=str(default_app.id),
        app_id=default_app.app_id,
        name=default_app.name,
        description=default_app.description,
        user_id=default_app.user_id,
        icon=default_app.icon,
        type=default_app.type,
        nodes=default_app.nodes,
        edges=default_app.edges,
        is_public=default_app.is_public,
        version=default_app.version,
    )
    return SuccessResponse(
        data=schema.model_dump(),
        msg="获取成功"
    )