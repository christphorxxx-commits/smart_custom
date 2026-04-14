# ============ Beanie MongoDB 数据模型 ============
from typing import Optional, Dict, Any

from bson import ObjectId

from backend.app.common.core.base_model import BaseMongoDocument


class ChatItem(BaseMongoDocument):
    """单条聊天消息记录"""
    chat_id: ObjectId           # 所属会话ID
    role: str                   # "user" - 用户提问, "assistant" - AI回复
    content: str                # 消息内容
    tokens: Optional[int] = None  # token计数（可选）
    metadata: Optional[Dict[str, Any]] = None  # 额外元数据

    class Settings:
        name = "chat_item"  # 集合名称

    model_config = {
        "arbitrary_types_allowed": True
    }


class Chat(BaseMongoDocument):
    """聊天会话（一个会话包含多条ChatItem）"""
    user_id: str                # 所属用户ID
    title: str                  # 会话标题（自动提取或用户修改）

    class Settings:
        name = "chat"  # 集合名称

    model_config = {
        "arbitrary_types_allowed": True
    }