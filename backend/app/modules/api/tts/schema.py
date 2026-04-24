# app/tts/schemas.py
from pydantic import BaseModel
from typing import Optional, Literal

class TTSRequest(BaseModel):
    """TTS 合成请求"""
    text: str
    model: str = "cosyvoice-v3-flash"
    voice: str = "longanyang"
    format: Literal["pcm", "wav"] = "pcm"  # 当前仅支持 pcm 流式

class TTSStartRequest(BaseModel):
    """启动 TTS 会话参数（用于 WebSocket）"""
    model: str = "cosyvoice-v3-flash"
    voice: str = "longanyang"

class TTSError(BaseModel):
    error: str
    code: Optional[int] = None