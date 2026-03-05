import asyncio

from fastapi import APIRouter,HTTPException,WebSocket,Query,WebSocketDisconnect
import uuid
from backend.app.common.core.core import logger
from backend.app.modules.asr.schema import ASRResult, ASRStartRequest
from backend.app.modules.asr.service import ASRService

ASRRouter = APIRouter(prefix="/ws", tags=["ASR"])
asr_service = ASRService()

@ASRRouter.websocket("/asr")
async def speech_to_text(
        websocket: WebSocket,
        model: str = Query("fun-asr-realtime"),
        sample_rate: int = Query(16000),
        format: str = Query("pcm")
):
    """
       WebSocket 接口：客户端发送音频流，服务端推送识别结果
       - 客户端先发一个空消息（或 start 消息）建立会话
       - 然后持续发送二进制音频数据（PCM 16k mono）
       - 服务端通过 text 消息推送 ASRResult（JSON）
       """
    await websocket.accept()
    session_id = str(uuid.uuid4())

    # 启动 ASR 流
    asr_stream = asr_service.start_streaming_asr(
        session_id=session_id,
        model=model,
        sample_rate=sample_rate,
        audio_format=format
    )

    # 启动结果推送任务
    async def push_results():
        async for result in asr_stream:
            if isinstance(result, Exception):
                await websocket.send_json({"error": str(result)})
                break
            await websocket.send_json(result.model_dump())

    push_task = asyncio.create_task(push_results())

    try:
        while True:
            # 接收音频数据（二进制）
            data = await websocket.receive_bytes()
            asr_service.send_audio_frame(session_id, data)
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        await websocket.send_json({"error": f"Server error: {str(e)}"})
    finally:
        asr_service.stop_session(session_id)
        push_task.cancel()


