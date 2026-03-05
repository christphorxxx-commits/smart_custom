# app/tts/controller.py
import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

from .service import TTSService
from .schema import TTSStartRequest

TTSRouter = APIRouter(prefix="ws",tags=["TTS"])
tts_service = TTSService()


@TTSRouter.websocket("/tts")
async def websocket_tts(
        websocket: WebSocket,
        model: str = Query("cosyvoice-v3-flash"),
        voice: str = Query("longanyang")
):
    """
    WebSocket TTS 接口：
    - 客户端连接后，发送 JSON 文本消息（如 {"text": "你好"}）
    - 服务端开始流式合成，并通过 binary 消息返回 PCM 音频
    - 支持多次发送文本（每次触发一次合成）
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())

    try:
        while True:
            # 接收客户端发来的文本（JSON 格式）
            message = await websocket.receive_json()
            text = message.get("text", "").strip()

            if not text:
                await websocket.send_json({"error": "Empty text"})
                continue

            print(f"🔊 TTS request: {text}")

            # 流式合成并推送音频
            async for chunk in tts_service.synthesize_stream(
                    session_id=session_id,
                    text=text,
                    model=model,
                    voice=voice
            ):
                if isinstance(chunk, bytes):
                    await websocket.send_bytes(chunk)
                else:  # TTSError
                    await websocket.send_json({"error": chunk.error})
                    break

    except WebSocketDisconnect:
        print(f"TTS client disconnected: {session_id}")
    except Exception as e:
        await websocket.send_json({"error": f"Server error: {str(e)}"})
    finally:
        tts_service.stop_session(session_id)