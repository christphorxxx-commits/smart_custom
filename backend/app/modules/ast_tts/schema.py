# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Any
# from enum import Enum
#
# class TTSVoiceEnum(str, Enum):
#     """TTS声音类型"""
#     CHERRY = "Cherry"
#     XIAOYI = "Xiaoyi"
#     XIAOYANG = "Xiaoyang"
#     CHENGUANG = "Chenguang"
#     YUEYANG = "Yueyang"
#
# class AudioFormatEnum(str, Enum):
#     """音频格式"""
#     MP3 = "mp3"
#     WAV = "wav"
#     PCM = "pcm"
#
# class TTSRequest(BaseModel):
#     """文字转语音请求模型"""
#     text: str = Field(..., min_length=1, max_length=2000, description="要转换的文本")
#     voice: TTSVoiceEnum = Field(default=TTSVoiceEnum.CHERRY, description="TTS声音类型")
#     format: AudioFormatEnum = Field(default=AudioFormatEnum.MP3, description="音频格式")
#     speed: float = Field(default=1.0, ge=0.5, le=2.0, description="语速倍率")
#     volume: float = Field(default=1.0, ge=0.0, le=2.0, description="音量倍率")
#     save_path: Optional[str] = Field(None, description="保存路径，如果为None则返回音频URL")
#
# class ASRRequest(BaseModel):
#     """语音转文字请求模型"""
#     audio_url: Optional[str] = Field(None, description="音频文件URL")
#     audio_path: Optional[str] = Field(None, description="音频文件路径")
#     language: Optional[str] = Field("zh", description="识别语言")
#
# class TTSResponse(BaseModel):
#     """文字转语音响应模型"""
#     success: bool
#     audio_url: Optional[str] = None
#     audio_path: Optional[str] = None
#     duration: Optional[float] = None
#     message: Optional[str] = None
#
# class ASRResponse(BaseModel):
#     """语音转文字响应模型"""
#     success: bool
#     text: Optional[str] = None
#     confidence: Optional[float] = None
#     language: Optional[str] = None
#     duration: Optional[float] = None
#     message: Optional[str] = None
#
# class WebSocketMessage(BaseModel):
#     """WebSocket消息模型"""
#     type: str = Field(..., description="消息类型: text, audio, command")
#     data: Any = Field(..., description="消息数据")
#     timestamp: float = Field(default_factory=lambda: __import__('time').time())
#
# class ServiceStatus(BaseModel):
#     """服务状态模型"""
#     status: str = Field(..., description="服务状态")
#     asr_available: bool = Field(..., description="ASR服务是否可用")
#     tts_available: bool = Field(..., description="TTS服务是否可用")
#     model_loaded: bool = Field(..., description="模型是否已加载")
#     active_connections: int = Field(..., description="活跃连接数")
#     uptime: float = Field(..., description="运行时间(秒)")
#     version: str = Field(default="1.0.0", description="版本号")
#
# class AudioConfig(BaseModel):
#     """音频配置模型"""
#     sample_rate: int = Field(default=24000, description="采样率")
#     channels: int = Field(default=1, description="声道数")
#     chunk_size: int = Field(default=1024, description="音频块大小")
#     format: str = Field(default="int16", description="音频格式")