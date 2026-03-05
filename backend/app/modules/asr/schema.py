# app/asr/schemas.py
from pydantic import BaseModel
from typing import Optional, Literal

class ASRStartRequest(BaseModel):
    """启动 ASR 会话的请求（可选参数）"""
    model: str = "fun-asr-realtime"
    sample_rate: int = 16000
    format: str = "pcm"

class ASRResult(BaseModel):
    """ASR 识别结果"""
    text: str
    is_final: bool
    request_id: Optional[str] = None
    timestamp: float  # Unix 时间戳

class ASRError(BaseModel):
    """错误信息"""
    error: str
    code: Optional[int] = None