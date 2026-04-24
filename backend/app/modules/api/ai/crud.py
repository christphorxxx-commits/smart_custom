from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from beanie import SortDirection

from backend.app.common.core.base_mongo_crud import BaseMongoCRUD
from backend.app.common.core.exceptions import CustomException
from backend.app.common.core.logger import log
from .model import Chat, ChatItem


from pydantic import BaseModel, Field

from ...module_system.auth.schema import AuthSchema


class ChatMongoCRUD(BaseMongoCRUD[Chat, BaseModel, BaseModel]):
    """
    聊天会话数据访问层 (MongoDB)

    负责操作 MongoDB 的 Chat 文档，存储聊天会话基本信息
    """

    def __init__(self, auth: AuthSchema):
        """
        初始化聊天会话CRUD
        """
        self.auth = auth
        super().__init__(model=Chat, auth=auth)

    async def get_or_create_chat_crud(
        self,
        chat_id: Optional[str],
        user_id: str,
        first_message: str
    ) -> Chat:
        """
        获取或创建一个聊天会话

        参数:
        - chat_id (Optional[str]): 会话ID，为空则创建新会话
        - uuid (str): 用户ID
        - first_message (str): 第一条消息，用于生成会话标题

        返回:
        - Chat: 聊天会话对象
        """
        if chat_id:
            # 查找已存在的会话
            try:
                chat = await self.get_by_id(chat_id)
                if chat and str(chat.user_id) == str(user_id):
                    # 更新更新时间
                    chat.updated_at = datetime.utcnow()
                    await chat.save()
                    return chat
            except Exception as e:
                # chat_id 格式不正确或不存在，创建新会话
                raise CustomException(str(e))

        # 创建新会话，标题自动取第一条消息前20个字
        title = first_message[:20] + ("..." if len(first_message) > 20 else "")
        data = {
            "user_id": user_id,
            "title": title,
            "created_by": user_id,
            "updated_by": user_id,
        }
        return await self.create(data)

    async def list_user_chats_crud(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Chat]:
        """
        获取用户的聊天会话列表

        参数:
        - user_id (str): 用户ID
        - skip (int): 跳过条数
        - limit (int): 返回条数

        返回:
        - List[Chat]: 聊天会话列表，按更新时间倒序
        """
        # Chat模型用户ID字段是user_id，不是uuid，所以需要自定义查询
        docs = await self.model.find(
            {"user_id": user_id, "is_deleted": False}
        ).sort([("updated_at", SortDirection.DESCENDING)]).skip(skip).limit(limit).to_list()
        return docs


class ChatItemMongoCRUD(BaseMongoCRUD[ChatItem, BaseModel, BaseModel]):
    """
    聊天消息数据访问层 (MongoDB)

    负责操作 MongoDB 的 ChatItem 文档，存储单条聊天消息
    """

    def __init__(self, auth: AuthSchema):
        """
        初始化聊天消息CRUD
        """
        super().__init__(model=ChatItem, auth=auth)

    async def save_message_crud(
        self,
        chat_id: ObjectId,
        role: str,
        content: str,
        tokens: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> ChatItem:
        """
        保存一条消息到对话记录

        参数:
        - chat_id (ObjectId): 所属会话ID
        - role (str): 消息角色 "user"/"assistant"
        - content (str): 消息内容
        - tokens (Optional[int]): token计数
        - metadata (Optional[dict]): 额外元数据

        返回:
        - ChatItem: 保存后的消息对象
        """
        data = {
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "tokens": tokens,
            "metadata": metadata,
        }
        return await self.create(data)

    async def get_chat_messages_crud(self, chat_id: ObjectId) -> List[ChatItem]:
        """
        获取会话的所有消息历史

        参数:
        - chat_id (ObjectId): 会话ID

        返回:
        - List[ChatItem]: 消息列表，按创建时间正序
        """
        messages = await self.model.find(
            {"chat_id": chat_id, "is_deleted": False}
        ).sort([("created_at", SortDirection.ASCENDING)]).to_list()
        return messages
