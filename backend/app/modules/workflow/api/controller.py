import json
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.response import SuccessResponse, ErrorResponse
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from backend.app.modules.workflow.api.crud import AppMongoCRUD, AppCRUD
from backend.app.modules.workflow.api.model import App
from backend.app.modules.workflow.api.schema import (
    CreateAppSchema, UpdateChatAgentSchema, UpdateWorkflowAgentSchema,
    AppDetailResponseSchema,
)
from backend.app.modules.workflow.api.service import AppService
from backend.app.modules.workflow.app import App
from backend.app.common.response import StreamResponse

# 内存缓存已编译的应用 {uuid: App}
app_storage: Dict[str, App] = {}

AppRouter = APIRouter(prefix="/app", tags=["App"])


def register_app(app: App) -> str:
    """注册一个app到缓存，返回uuid"""
    app_storage[app.uuid] = app
    return app.uuid


@AppRouter.post("/chat/{app_id}")
async def create_chat(
        app_id: str,
        query: ChatQuerySchema,
        db: AsyncSession = Depends(db_getter),
) -> StreamResponse:
    """
    HTTP流式运行应用
    - uuid: 应用UUID（路径参数，MongoDB中的app_id）
    - query: 请求body，包含message
    - 返回: 流式token输出，每个chunk是一个token片段
    """
    # 从缓存获取已编译的app，如果找不到从MongoDB加载
    if app_id not in app_storage:
        # 从MongoDB根据app_id获取完整配置
        app_mongo_crud = AppMongoCRUD()
        mongo_app = await app_mongo_crud.get_app_by_appid_crud(app_id)
        if not mongo_app:
            # 如果MongoDB中找不到，返回错误（但StreamResponse需要yield，这里简化处理）
            async def generate_error():
                data = json.dumps("应用不存在，请检查配置", ensure_ascii=False)
                yield f"data: {data}\n\n".encode('utf-8')

            return StreamResponse(generate_error(), media_type="text/event-stream; charset=utf-8")

        # 格式转换：处理旧数据/各种前端格式，保证总能得到正确格式
        def convert_node(node: dict) -> dict:
            """转换 node 类型，if → router"""
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
            """转换 edge 字段名 sourceNodeId → source"""
            source = edge.get("source") or edge.get("sourceNodeId", "")
            target = edge.get("target") or edge.get("targetNodeId", "")
            return {
                "source": source,
                "target": target,
                "type": edge.get("type", "normal"),
                "condition": edge.get("condition", None)
            }

        # 转换所有节点和边（兼容旧数据格式）
        converted_nodes = [convert_node(n) for n in mongo_app.nodes]
        converted_edges = [convert_edge(e) for e in mongo_app.edges]

        # 将MongoDB文档转换为 App 对象
        app_data = {
            "name": mongo_app.name,
            "description": mongo_app.description,
            "uuid": mongo_app.uuid,
            "nodes": converted_nodes,
            "edges": converted_edges,
        }
        app = App.model_validate(app_data)
        app_id = register_app(app)
    else:
        app = app_storage[app_id]

    # 使用异步迭代，逐token输出，真正的流式响应（SSE格式）
    async def generate():
        # 是否是第一个token，用于去掉开头的markdown标题符号
        is_first = True
        async for event in app.astream_tokens({"input": query.message}):
            if event["type"] == "token":
                # SSE 格式：直接输出纯文本 token，不需要 JSON 包装
                data = event["token"]
                # 去掉开头的 markdown 标题符号 ## 等
                if is_first:
                    # 去掉开头连续的 # 和空格
                    data = data.lstrip('# ')
                    is_first = False
                # 如果data为空，跳过不输出
                if data:
                    yield f"data: {data}\n\n".encode('utf-8')

    return StreamResponse(generate(), media_type="text/event-stream; charset=utf-8")


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


@AppRouter.post("/save", description="保存画板中的app")
async def save_app(
        data: CreateAppSchema,
        db: AsyncSession = Depends(db_getter),
        current_user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """保存画板中的工作流应用"""
    auth = AuthSchema(db=db, user=current_user)
    result = await AppService.save_app(auth=auth, user=current_user, data=data)

    return SuccessResponse(
        data=result,
        msg="保存成功"
    )


@AppRouter.get("/{app_id}", summary="根据app_id获取应用详情")
async def get_app_detail(
        app_id: str,
        db: AsyncSession = Depends(db_getter),
        current_user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """
    根据app_id (UUID) 获取应用完整详情
    - uuid: MongoDB 中的应用UUID
    - 返回: 完整应用信息，包含nodes和edges
    """
    # 先从 PostgreSQL 根据 uuid 找到 PG 记录，获取 PG id
    auth = AuthSchema(db=db, user=current_user)
    app_crud = AppCRUD(auth)
    pg_app = await app_crud.get_app_by_app_id_crud(app_id)

    # 从MongoDB直接获取完整配置
    mongo_app = await AppService.get_app_by_app_id(app_id)
    if not mongo_app:
        return ErrorResponse(msg="应用配置不存在")

    # 使用 AppDetailResponseSchema 构建响应
    # 只返回前端编辑需要的字段：
    # - 基本信息 (name, description, icon, type, is_public)
    # - 工作流数据 (nodes, edges)
    # - 所有系统配置字段
    response_data = AppDetailResponseSchema(
        name=mongo_app.name,
        description=mongo_app.description,
        user_id=mongo_app.user_id,
        icon=mongo_app.icon,
        type=mongo_app.type,
        is_public=mongo_app.is_public,
        nodes=mongo_app.nodes,
        edges=mongo_app.edges,
        version=mongo_app.version,
        # 通用系统配置
        enableFileUpload=mongo_app.enableFileUpload,
        globalVariables=mongo_app.globalVariables,
        openingMessage=mongo_app.openingMessage,
        enableTTS=mongo_app.enableTTS,
        enableASR=mongo_app.enableASR,
        guessedQuestions=mongo_app.guessedQuestions,
        inputGuidance=mongo_app.inputGuidance,
        # 工作流特有配置
        timeExecute=mongo_app.timeExecute,
        autoExecute=mongo_app.autoExecute,
        # 对话式 Agent 特有配置
        llmConfig=mongo_app.llmConfig,
        enableKnowledgeBase=mongo_app.enableKnowledgeBase,
        knowledgeBaseConfig=mongo_app.knowledgeBaseConfig,
        enableToolCall=mongo_app.enableToolCall,
    )

    return SuccessResponse(
        data=response_data.model_dump(),
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
    result = await AppService.create_app(auth=auth, user=current_user, data=data)
    return SuccessResponse(
        data=result,
        msg="创建成功"
    )


@AppRouter.post("/update", description="更新工作流应用")
async def update_app(
        data: UpdateWorkflowAgentSchema | UpdateChatAgentSchema,
        db: AsyncSession = Depends(db_getter),
        current_user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """更新现有工作流应用"""
    auth = AuthSchema(db=db, user=current_user)
    result = await AppService.update_app(auth=auth, user=current_user, data=data)
    return SuccessResponse(
        data=result,
        msg="更新成功"
    )
