import asyncio
import json
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from sqlalchemy import select

from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.response import SuccessResponse, ErrorResponse
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.model import AiApp, App
from backend.app.modules.workflow.app import App
from backend.app.modules.workflow.crud import AppCRUD
from backend.app.modules.workflow.service import AppService
from backend.app.modules.workflow.schema import CreateWorkflowSchema, UpdateWorkflowSchema
# from backend.app.common.core.db.session import async_session

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

#
# @AppRouter.websocket("/stream/{app_id}")
# async def stream_workflow(
#     websocket: WebSocket,
#     app_id: str,
#     input: str = Query(...),
# ):
#     """
#     WebSocket流式运行workflow
#     - app_id: workflow应用ID
#     - input: 用户输入
#     - 服务端逐token推送事件:
#       {"type": "token", "token": "text", "full_content": "...", "node_id": "..."}
#       {"type": "node_complete", "node_id": "...", "output": {...}}
#       {"type": "workflow_complete", "final_output": "...", "final_state": {...}}
#       {"type": "error", "message": "error message"}
#     """
#     await websocket.accept()
#
#     # 检查app_id是否存在
#     if app_id not in workflow_storage:
#         await websocket.send_json({
#             "type": "error",
#             "message": f"Workflow app_id {app_id} not found"
#         })
#         await websocket.close()
#         return
#
#     app = workflow_storage[app_id]
#
#     try:
#         # 流式运行，逐个发送事件
#         async for event in app.astream_tokens({"input": input}):
#             await websocket.send_json(event)
#             # 给WebSocket一点呼吸空间，避免拥塞
#             await asyncio.sleep(0)
#
#         # 完成后可以关闭
#         await asyncio.sleep(0)
#
#     except WebSocketDisconnect:
#         # 客户端断开，正常退出
#         pass
#     except Exception as e:
#         await websocket.send_json({
#             "type": "error",
#             "message": f"Server error: {str(e)}"
#         })


# @AppRouter.websocket("/create_and_stream")
# async def create_and_stream(
#     websocket: WebSocket,
# ):
#     """
#     创建workflow并立即流式运行
#     - 客户端先发送创建请求JSON: {"workflow_data": {...}, "input": "..."}
#     - 服务端开始流式输出，和 /stream/{app_id} 一样的事件格式
#     """
#     await websocket.accept()
#
#     try:
#         # 接收客户端发送的初始化数据
#         data = await websocket.receive_text()
#         init_data = json.loads(data)
#         workflow_data = init_data["workflow_data"]
#         input_text = init_data.get("input", "")
#
#         # 创建App对象
#         app = App.model_validate(workflow_data)
#         app_id = register_workflow(app)
#
#         # 返回app_id给客户端
#         await websocket.send_json({
#             "type": "created",
#             "app_id": app_id
#         })
#         await asyncio.sleep(0)
#
#         # 开始流式运行
#         async for event in app.astream_tokens({"input": input_text}):
#             await websocket.send_json(event)
#             await asyncio.sleep(0)
#
#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         await websocket.send_json({
#             "type": "error",
#             "message": f"Server error: {str(e)}"
#         })


@AppRouter.get("/list", summary="获取当前用户可用的应用列表")
async def list_apps(
    current_user: UserModel = Depends(get_current_user),
    db : AsyncSession = Depends(db_getter),
) -> SuccessResponse:
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


# @AppRouter.delete("/{app_id}")
# async def delete_workflow(app_id: str):
#     """删除一个workflow (内存缓存)"""
#     if app_id in workflow_storage:
#         del workflow_storage[app_id]
#         return {"success": True, "message": f"Workflow {app_id} deleted"}
#     return {"success": False, "message": f"Workflow {app_id} not found"}


# ============ 持久化到MongoDB接口 ============

# @AppRouter.post("/save", summary="保存工作流应用到MongoDB + PG")
# async def save_workflow(
#     data: CreateWorkflowSchema,
#     current_user: UserModel = Depends(get_current_user)
# ) -> SuccessResponse:
#     """
#     保存工作流应用：
#     1. 保存完整配置到 MongoDB apps 集合
#     2. 保存基本信息到 PostgreSQL app 表（用于权限查询和列表）
#     """
#     # 1. 创建并保存到 MongoDB
#     app = await AppCRUD.create_app(
#         user_id=str(current_user.id),
#         name=data.name,
#         description=data.description,
#         nodes=data.nodes,
#         edges=data.edges,
#         icon=data.icon,
#         is_public=data.is_public,
#     )
#
#     # 2. 同时保存基本信息到 PostgreSQL app 表
#     from backend.app.common.core.db.session import async_session
#     async with async_session() as session:
#         pg_app = AiApp(
#             app_id=app.app_id,
#             name=data.name,
#             user_id=current_user.id,
#             description=data.description,
#             icon=data.icon,
#             is_public=data.is_public,
#             type="workflow",
#         )
#         session.add(pg_app)
#         await session.commit()
#
#     return SuccessResponse(
#         data={
#             "id": str(app.id),
#             "app_id": app.app_id,
#             "name": app.name,
#         },
#         msg="保存成功"
#     )


# @AppRouter.put("/{workflow_id}", summary="更新工作流")
# async def update_workflow(
#     workflow_id: str,
#     data: UpdateWorkflowSchema,
#     current_user: UserModel = Depends(get_current_user)
# ) -> JSONResponse:
#     """更新已保存的工作流"""
#     app = await AppCRUD.update_workflow(
#         workflow_id=workflow_id,
#         user_id=str(current_user.id),
#         **data.model_dump(exclude_unset=True)
#     )
#     if not app:
#         return ErrorResponse(msg="工作流不存在或无权限")
#     return SuccessResponse(
#         data={
#             "id": str(app.id),
#             "app_id": app.app_id,
#             "name": app.name,
#         },
#         msg="更新成功"
#     )
#

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


# @AppRouter.get("/detail/{app_id}", summary="根据app_id获取应用完整配置（从MongoDB）")
# async def get_app_detail(
#     app_id: str,
#     current_user: UserModel = Depends(get_current_user)
# ) -> JSONResponse:
#     """
#     根据app_id从MongoDB获取应用完整配置（nodes, edges等）
#
#     查询流程：
#     1. 根据app_id查询MongoDB中的App文档
#     2. 检查权限：公开或创建者本人可访问
#     3. 返回完整配置给前端
#     """
#     # 在MongoDB中 app.app_id = 我们要查询的 app_id
#     # 需要查询 app collection where app_id == app_id
#     from pymongo import MongoClient
#     from backend.app.config.setting import settings
#     client = MongoClient(settings.MONGO_URL)
#     db = client[settings.MONGO_DB_NAME]
#     collection = db['apps']
#
#     app_doc = collection.find_one({"app_id": app_id, "is_deleted": False})
#     if not app_doc:
#         return ErrorResponse(msg="应用不存在")
#
#     # 检查权限
#     if not app_doc.get("is_public", False) and str(app_doc.get("user_id")) != str(current_user.id):
#         return ErrorResponse(msg="无权限访问此应用")
#
#     return SuccessResponse(
#         data={
#             "id": str(app_doc["_id"]),
#             "app_id": app_doc["app_id"],
#             "name": app_doc["name"],
#             "description": app_doc.get("description"),
#             "icon": app_doc.get("icon", "🤖"),
#             "is_public": app_doc.get("is_public", False),
#             "type": app_doc.get("type", "workflow"),
#             "created_at": app_doc.get("created_at"),
#             "updated_at": app_doc.get("updated_at"),
#             "nodes": app_doc["nodes"],
#             "edges": app_doc["edges"],
#         },
#         msg="获取成功"
#     )

# @AppRouter.get("/{workflow_id}", summary="获取工作流详情(按MongoDB ID)")
# async def get_workflow_detail(
#     workflow_id: str,
#     current_user: UserModel = Depends(get_current_user)
# ) -> JSONResponse:
#     """获取工作流完整配置（按MongoDB ID）"""
#     app = await AppCRUD.get_by_id(workflow_id)
#     if not app:
#         return ErrorResponse(msg="工作流不存在")
#     # 检查权限：公开或者是自己创建的
#     if not app.is_public and str(app.user_id) != str(current_user.id):
#         return ErrorResponse(msg="无权限访问此工作流")
#     return SuccessResponse(
#         data={
#             "id": str(app.id),
#             "app_id": app.app_id,
#             "name": app.name,
#             "description": app.description,
#             "icon": app.icon,
#             "is_public": app.is_public,
#             "created_at": app.created_at,
#             "updated_at": app.updated_at,
#             "version": app.version,
#             "nodes": app.nodes,
#             "edges": app.edges,
#         },
#         msg="获取成功"
#     )


# @AppRouter.delete("/{workflow_id}/persist", summary="删除MongoDB中的工作流")
# async def delete_workflow_persist(
#     workflow_id: str,
#     current_user: UserModel = Depends(get_current_user)
# ) -> JSONResponse:
#     """从MongoDB删除工作流"""
#     success, msg = await AppCRUD.delete_workflow(workflow_id, str(current_user.id))
#     if success:
#         # 同时删除内存缓存
#         app = await AppCRUD.get_by_id(workflow_id)
#         if app and app.app_id in workflow_storage:
#             del workflow_storage[app.app_id]
#         return SuccessResponse(msg=msg)
#     return ErrorResponse(msg=msg)
