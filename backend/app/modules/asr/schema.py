from pydantic import BaseModel,Field
from typing import Optional,Any

class ASRRequest(BaseModel):

    """语音转文字请求模型"""
    audio_url: Optional[str] = Field(None, description="音频文件URL")
    audio_path: Optional[str] = Field(None, description="音频文件路径")
    language: Optional[str] = Field("zh", description="识别语言")


class ASRResponse(BaseModel):
    """语音转文字响应模型"""
    success: bool
    text: Optional[str] = None
    confidence: Optional[float] = None
    language: Optional[str] = None
    duration: Optional[float] = None
    message: Optional[str] = None


class AudioConfig(BaseModel):
    """音频配置模型"""
    sample_rate: int = Field(default=24000, description="采样率")
    channels: int = Field(default=1, description="声道数")
    chunk_size: int = Field(default=1024, description="音频块大小")
    format: str = Field(default="int16", description="音频格式")