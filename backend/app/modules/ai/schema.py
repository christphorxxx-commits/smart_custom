from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatQuerySchema(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, max_length=4000, description="聊天消息")
    session_id: Optional[str] = Field(None, description="会话ID，用于保持上下文")
    context: Optional[Dict[str, Any]] = Field(None, description="额外上下文信息")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool = Field(..., description="请求是否成功")
    text: str = Field(..., description="AI回复的文本")
    session_id: Optional[str] = Field(None, description="会话ID")
    context: Optional[Dict[str, Any]] = Field(None, description="返回的上下文信息")
    message: Optional[str] = Field(None, description="错误或状态信息")
