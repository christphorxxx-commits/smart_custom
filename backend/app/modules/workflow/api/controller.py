import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse
from starlette.responses import JSONResponse

from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.core.logger import log
from backend.app.common.response import SuccessResponse, ErrorResponse
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.api.schema import (
    CreateAppSchema, UpdateAgentSchema,
)
from backend.app.modules.workflow.api.service import AppService

AppRouter = APIRouter(prefix="/app", tags=["App"])


# 参照 AI chat_sse 接口，使用 EventSourceResponse 返回流式 token
@AppRouter.post("/chat/{uuid}", summary="工作流对话(SSE)", description="运行工作流对话，服务器发送事件版本")
async def create_chat(
        uuid: str,
        query: ChatQuerySchema,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(db_getter),
) -> EventSourceResponse:
    """
    HTTP流式运行应用
    - uuid: 应用UUID（路径参数，MongoDB中的app_id）
    - query: 请求body，包含message
    - 返回: 流式token输出，每个chunk是一个token片段
    """
    user_name = current_user.username if current_user else "未知用户"
    log.info(f"用户 {user_name} 发起工作流对话(SSE): uuid={uuid}, message={query.message[:50]}...")
    auth = AuthSchema(user=current_user,db=db)
    # 获取编译好的 App 实例（service 层处理缓存）
    app = await AppService.exist(auth,uuid)

    if not app:
        # 如果MongoDB中找不到，返回错误
        async def generate_error():
            yield {
                "data": "应用不存在，请检查配置",
                "event": "error"
            }
        return EventSourceResponse(
            generate_error(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            })

    # 返回 EventSourceResponse 包装异步生成器
    return EventSourceResponse(
        AppService.chat_sse(app, query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# 保留原方法（注释掉不删除）
# @AppRouter.post("/chat/{uuid}")
# async def create_chat(
#         uuid: str,
#         query: ChatQuerySchema,
# ) -> StreamResponse:
#     """
#     HTTP流式运行应用
#     - uuid: 应用UUID（路径参数，MongoDB中的app_id）
#     - query: 请求body，包含message
#     - 返回: 流式token输出，每个chunk是一个token片段
#     """
#     # 从MongoDB加载应用配置
#     app_mongo_crud = AppMongoCRUD()
#     mongo_app = await app_mongo_crud.get_app_by_uuid_crud(uuid)
#     if not mongo_app:
#         return StreamResponse(generate_error(), media_type="text/event-stream; charset=utf-8")
#
#     # 前端格式已经统一，直接使用 MongoDB 中保存的原始数据（包含 x y 坐标）
#     # 不需要格式转换，nodes 已经是正确格式：id/type/x/y/config
#     app_data = {
#         "name": mongo_app.name,
#         "description": mongo_app.description,
#         "uuid": mongo_app.uuid,
#         "nodes": mongo_app.nodes,
#         "edges": mongo_app.edges,
#     }
#     app = App(**app_data)
#     # 注册到缓存
#     uuid = register_app(app)
#
#     # 使用异步迭代，逐token输出，真正的流式响应（SSE格式）
#     async def generate():
#         # 是否是第一个token，用于去掉开头的markdown标题符号
#         is_first = True
#         async for event in app.astream_tokens({"input": query.message}):
#             if event["type"] == "token":
#                 # SSE 格式：直接输出纯文本 token，不需要 JSON 包装
#                 data = event["token"]
#                 # 去掉开头的 markdown 标题符号 ## 等
#                 if is_first:
#                     # 去掉开头连续的 # 和空格
#                     data = data.lstrip('# ')
#                     is_first = False
#                 # 如果data为空，跳过不输出
#                 if data:
#                     yield f"data: {data}\n\n".encode('utf-8')
#
#     return StreamResponse(generate(), media_type="text/event-stream; charset=utf-8")


@AppRouter.get("/list", summary="获取当前用户可用的应用列表")
async def list_apps(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(db_getter),
) -> JSONResponse:
    """
    获取当前用户有权限可以使用的所有应用

    权限规则：
    - 用户自己创建的所有应用（不管是否公开）
    - 所有其他用户创建的公开应用
    """

    auth = AuthSchema(db=db, user=current_user)

    data = await AppService.get_available_apps(auth)
    return SuccessResponse(
        data=data,
        msg="获取成功"
    )


@AppRouter.get("/default", summary="获取默认示例工作流")
async def get_default_workflow(
        db: AsyncSession = Depends(db_getter),
) -> JSONResponse:
    """获取默认示例工作流（用于编辑器加载默认配置）"""
    # 直接返回默认示例工作流的定义，不需要从数据库读取
    # 这个示例用于展示条件分支路由功能
    default_data = {
        "uuid": "8488bff8-30a2-415d-8d1d-7c4fb4b6567b",
        "name": "示例工作流",
        "description": "这是一个示例条件分支工作流，展示多分支路由能力",
        "icon": "🌐",
        "type": "WORKFLOW",
        "is_deleted": False,
        "status": "active",
        "nodes": [
            {"id": "start", "type": "start", "config": {}},
            {
                "id": "router",
                "type": "router",
                "config": {"options": ["story", "joke", "poem"]}
            },
            {
                "id": "story_node",
                "type": "llm",
                "config": {
                    "model": "qwen-max",
                    "systemPrompt": "写一个故事：{input}",
                    "temperature": 0.7,
                    "maxTokens": 2000
                }
            },
            {
                "id": "joke_node",
                "type": "llm",
                "config": {
                    "model": "qwen-max",
                    "systemPrompt": "讲一个笑话：{input}",
                    "temperature": 0.9,
                    "maxTokens": 500
                }
            },
            {
                "id": "poem_node",
                "type": "llm",
                "config": {
                    "model": "qwen-max",
                    "systemPrompt": "写一首诗：{input}",
                    "temperature": 0.8,
                    "maxTokens": 1000
                }
            },
            {"id": "end", "type": "end", "config": {}}
        ],
        "edges": [
            {"source": "start", "target": "router", "type": "normal", "condition": None},
            {"source": "router", "target": "story_node", "type": "conditional", "condition": "story"},
            {"source": "router", "target": "joke_node", "type": "conditional", "condition": "joke"},
            {"source": "router", "target": "poem_node", "type": "conditional", "condition": "poem"},
            {"source": "story_node", "target": "end", "type": "normal", "condition": None},
            {"source": "joke_node", "target": "end", "type": "normal", "condition": None},
            {"source": "poem_node", "target": "end", "type": "normal", "condition": None}
        ],
        "is_public": True,
        "version": 1,
        "enableFileUpload": False,
        "globalVariables": {},
        "enableTTS": False,
        "enableASR": False,
        "guessedQuestions": False,
        "inputGuidance": False,
        "timeExecute": False,
        "autoExecute": False
    }
    return SuccessResponse(
        data=default_data,
        msg="获取成功"
    )


@AppRouter.get("/{uuid}", summary="根据app_id获取应用详情")
async def get_app_detail(
        uuid: str,
        db: AsyncSession = Depends(db_getter),
        current_user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """
    根据app_id (UUID) 获取应用完整详情
    - uuid: MongoDB 中的应用UUID
    - 返回: 完整应用信息，包含nodes和edges
    """
    auth = AuthSchema(db=db, user=current_user)
    result = await AppService.get_app_detail(auth=auth,uuid=uuid)

    if not result:
        return ErrorResponse(msg="应用配置不存在")

    return SuccessResponse(
        data=result,
        msg="获取成功"
    )


@AppRouter.post("/create", description="创建新的Agent应用")
async def create_app(
        data: CreateAppSchema,
        db: AsyncSession = Depends(db_getter),
        current_user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """创建新的空白工作流应用"""
    auth = AuthSchema(db=db, user=current_user)
    result = await AppService.create_app(auth=auth, data=data)
    return SuccessResponse(
        data=result,
        msg="创建成功"
    )


@AppRouter.post("/update", description="更新工作流应用")
async def update_app(
        data: UpdateAgentSchema,
        db: AsyncSession = Depends(db_getter),
        current_user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """更新现有工作流应用"""
    print(data)
    auth = AuthSchema(db=db, user=current_user)
    result = await AppService.update_app(auth=auth, user=current_user, data=data)
    return SuccessResponse(
        data=result,
        msg="更新成功"
    )
