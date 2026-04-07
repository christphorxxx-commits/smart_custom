from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from beanie import Document
from bson import ObjectId


# ============ Pydantic 请求/响应模型 ============
class ChatQuerySchema(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, max_length=4000, description="聊天消息")
    chat_id: Optional[str] = Field(None, description="会话ID，用于保持上下文")
    context: Optional[Dict[str, Any]] = Field(None, description="额外上下文信息")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool = Field(..., description="请求是否成功")
    text: str = Field(..., description="AI回复的文本")
    chat_id: Optional[str] = Field(None, description="会话ID")
    context: Optional[Dict[str, Any]] = Field(None, description="返回的上下文信息")
    message: Optional[str] = Field(None, description="错误或状态信息")


class ChatListResponseItem(BaseModel):
    """聊天列表项响应模型"""
    id: str = Field(..., description="会话ID")
    title: str = Field(..., description="会话标题")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")


class ChatListResponse(BaseModel):
    """聊天列表响应模型"""
    success: bool = Field(True, description="请求是否成功")
    data: list[ChatListResponseItem] = Field([], description="会话列表")
    total: int = Field(..., description="总数")


class ChatMessageResponseItem(BaseModel):
    """单条消息响应模型"""
    role: str = Field(..., description="角色 user/assistant")
    content: str = Field(..., description="消息内容")
    created_at: datetime = Field(..., description="创建时间")


class ChatMessageListResponse(BaseModel):
    """消息历史响应模型"""
    success: bool = Field(True, description="请求是否成功")
    title: str = Field(..., description="会话标题")
    data: list[ChatMessageResponseItem] = Field([], description="消息列表")


class BasicResponse(BaseModel):
    """基础操作响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field("", description="提示信息")

# ============ Beanie MongoDB 数据模型 ============
class ChatItem(Document):
    """单条聊天消息记录"""
    chat_id: ObjectId           # 所属会话ID
    role: str                   # "user" - 用户提问, "assistant" - AI回复
    content: str                # 消息内容
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tokens: Optional[int] = None  # token计数（可选）
    metadata: Optional[Dict[str, Any]] = None  # 额外元数据

    class Settings:
        name = "chat_item"  # 集合名称

    model_config = {
        "arbitrary_types_allowed": True
    }


class Chat(Document):
    """聊天会话（一个会话包含多条ChatItem）"""
    user_id: str                # 所属用户ID
    title: str                  # 会话标题（自动提取或用户修改）
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = False    # 软删除

    class Settings:
        name = "chat"  # 集合名称

    model_config = {
        "arbitrary_types_allowed": True
    }
