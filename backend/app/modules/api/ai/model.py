# ============ Beanie MongoDB 数据模型 ============
from datetime import datetime
from typing import Optional, Dict, Any

from beanie import Document
from bson import ObjectId
from pydantic import Field



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