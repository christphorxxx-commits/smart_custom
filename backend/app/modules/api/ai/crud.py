from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from .model import Chat,ChatItem
from backend.app.common.core.logger import log


class AICRUD:
    """AI聊天数据访问层"""

    @staticmethod
    async def get_or_create_chat(
        chat_id: Optional[str],
        user_id: str,
        first_message: str
    ) -> Chat:
        """获取或创建一个聊天会话"""
        if chat_id:
            # 查找已存在的会话
            try:
                chat = await Chat.get(ObjectId(chat_id))
                if chat and not chat.is_deleted and str(chat.user_id) == str(user_id):
                    # 更新更新时间
                    chat.updated_at = datetime.utcnow()
                    await chat.save()
                    return chat
            except Exception:
                # chat_id 格式不正确或不存在，创建新会话
                pass

        # 创建新会话，标题自动取第一条消息前20个字
        title = first_message[:20] + ("..." if len(first_message) > 20 else "")
        chat = Chat(
            user_id=user_id,
            title=title
        )
        await chat.insert()
        return chat

    @staticmethod
    async def save_message(
        chat_id: ObjectId,
        role: str,
        content: str
    ) -> ChatItem:
        """保存一条消息到对话记录"""
        item = ChatItem(
            chat_id=chat_id,
            role=role,
            content=content
        )
        await item.insert()
        return item

    @staticmethod
    async def update_chat_time(chat_id: ObjectId) -> None:
        """更新会话最后更新时间"""
        chat = await Chat.get(chat_id)
        if chat:
            chat.updated_at = datetime.utcnow()
            await chat.save()

    @staticmethod
    async def list_user_chats(
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Chat]:
        """获取用户的聊天会话列表"""
        chats = await Chat.find(
            {"user_id": user_id, "is_deleted": False}
        ).sort([("updated_at", -1)]).skip(skip).limit(limit).to_list()
        return chats

    @staticmethod
    async def get_chat_messages(chat_id: ObjectId) -> List[ChatItem]:
        """获取会话的所有消息历史，按时间正序"""
        messages = await ChatItem.find(
            {"chat_id": chat_id}
        ).sort([("created_at", 1)]).to_list()
        return messages

    @staticmethod
    async def delete_chat(chat_id: ObjectId, user_id: str) -> tuple[bool, str]:
        """软删除聊天会话"""
        try:
            chat = await Chat.get(chat_id)
            if not chat:
                return False, "会话不存在"
            if chat.is_deleted:
                return False, "会话已删除"
            if str(chat.user_id) != str(user_id):
                return False, "无权限删除此会话"

            chat.is_deleted = True
            await chat.save()
            return True, "删除成功"
        except Exception as e:
            log.error(f"删除会话出错: {e}", exc_info=True)
            return False, str(e)
