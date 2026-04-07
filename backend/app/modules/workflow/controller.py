import asyncio
import json
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from pydantic import BaseModel

from backend.app.common.response import StreamResponse
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.workflow.app import App

# 内存存储已创建的Workflow应用 {app_id: App}
workflow_storage: Dict[str, App] = {}

WorkflowRouter = APIRouter(prefix="/workflow", tags=["Workflow"])


class WorkflowCreateRequest(BaseModel):
    """创建workflow请求"""
    workflow_data: dict  # 整个workflow的json配置


def register_workflow(app: App) -> str:
    """注册一个workflow到存储，返回app_id"""
    if not app.app_id:
        from backend.app.common.utils.common_util import uuid4_str
        app.app_id = uuid4_str()
    workflow_storage[app.app_id] = app
    return app.app_id
from pathlib import Path
from backend.app.common.response import StreamResponse

@WorkflowRouter.post("/chat/{app_id}")
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

    # 使用异步迭代，逐token输出，真正的流式响应
    async def generate():
        async for event in app.astream_tokens({"input": query.message}):
            if event["type"] == "token":
                yield event["token"].encode('utf-8')

    return StreamResponse(generate(), media_type="text/plain; charset=utf-8")


@WorkflowRouter.websocket("/stream/{app_id}")
async def stream_workflow(
    websocket: WebSocket,
    app_id: str,
    input: str = Query(...),
):
    """
    WebSocket流式运行workflow
    - app_id: workflow应用ID
    - input: 用户输入
    - 服务端逐token推送事件:
      {"type": "token", "token": "text", "full_content": "...", "node_id": "..."}
      {"type": "node_complete", "node_id": "...", "output": {...}}
      {"type": "workflow_complete", "final_output": "...", "final_state": {...}}
      {"type": "error", "message": "error message"}
    """
    await websocket.accept()

    # 检查app_id是否存在
    if app_id not in workflow_storage:
        await websocket.send_json({
            "type": "error",
            "message": f"Workflow app_id {app_id} not found"
        })
        await websocket.close()
        return

    app = workflow_storage[app_id]

    try:
        # 流式运行，逐个发送事件
        async for event in app.astream_tokens({"input": input}):
            await websocket.send_json(event)
            # 给WebSocket一点呼吸空间，避免拥塞
            await asyncio.sleep(0)

        # 完成后可以关闭
        await asyncio.sleep(0)

    except WebSocketDisconnect:
        # 客户端断开，正常退出
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Server error: {str(e)}"
        })


@WorkflowRouter.websocket("/create_and_stream")
async def create_and_stream(
    websocket: WebSocket,
):
    """
    创建workflow并立即流式运行
    - 客户端先发送创建请求JSON: {"workflow_data": {...}, "input": "..."}
    - 服务端开始流式输出，和 /stream/{app_id} 一样的事件格式
    """
    await websocket.accept()

    try:
        # 接收客户端发送的初始化数据
        data = await websocket.receive_text()
        init_data = json.loads(data)
        workflow_data = init_data["workflow_data"]
        input_text = init_data.get("input", "")

        # 创建App对象
        app = App.model_validate(workflow_data)
        app_id = register_workflow(app)

        # 返回app_id给客户端
        await websocket.send_json({
            "type": "created",
            "app_id": app_id
        })
        await asyncio.sleep(0)

        # 开始流式运行
        async for event in app.astream_tokens({"input": input_text}):
            await websocket.send_json(event)
            await asyncio.sleep(0)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Server error: {str(e)}"
        })


@WorkflowRouter.get("/list")
async def list_workflows():
    """列出所有已创建的workflow"""
    return {
        "app_ids": list(workflow_storage.keys()),
        "count": len(workflow_storage)
    }


@WorkflowRouter.delete("/{app_id}")
async def delete_workflow(app_id: str):
    """删除一个workflow"""
    if app_id in workflow_storage:
        del workflow_storage[app_id]
        return {"success": True, "message": f"Workflow {app_id} deleted"}
    return {"success": False, "message": f"Workflow {app_id} not found"}
