from bson import ObjectId
from backend.app.common.core.core import tongyillm
from backend.app.modules.api.ai.crud import AICRUD
from backend.app.modules.api.ai.schema import ChatQuerySchema, Chat, ChatItem
from backend.app.common.core.logger import log


class AIService:
    """AI聊天服务层"""

    @classmethod
    def chat_service(cls, query: ChatQuerySchema):
        """
        处理聊天查询
        :param query: 聊天查询模型
        :return: 生成器，每次返回一个聊天响应
        """
        try:
            #处理消息
            from langchain_core.messages import HumanMessage
            message = HumanMessage(content=query.message)
            for response in tongyillm.stream([message]):
                yield response.content

        except Exception as e:
            log.error(f"AI对话出现问题: {e}", exc_info=True)

    @classmethod
    async def chat_stream_generator(cls, query: ChatQuerySchema):
        """
        异步流式生成，保存AI回复到MongoDB后完成
        :param query: 聊天查询
        :param chat_id: 会话ID
        :yield: 每个token字节
        """
        from langchain_core.messages import HumanMessage
        message = HumanMessage(content=query.message)
        full_response = ""

        try:
            for response in tongyillm.stream([message]):
                if response.content:
                    full_response += response.content
                    yield response.content.encode('utf-8')

            # 流式完成，保存完整AI回复
            if full_response:
                await cls.save_message(ObjectId(query.chat_id), "assistant", full_response)
                await cls.update_chat_time(ObjectId(query.chat_id))

        except Exception as e:
            log.error(f"AI流式生成出错: {e}", exc_info=True)
            error_msg = f"抱歉，处理您的请求时出现了错误：{str(e)}"
            yield error_msg.encode("utf-8")

    @classmethod
    async def get_or_create_chat(cls, chat_id: str | None, user_id: str, first_message: str) -> Chat:
        """获取或创建一个聊天会话"""
        return await AICRUD.get_or_create_chat(chat_id, user_id, first_message)

    @classmethod
    async def save_message(cls, chat_id: ObjectId, role: str, content: str) -> ChatItem:
        """保存一条消息到对话记录"""
        return await AICRUD.save_message(chat_id, role, content)

    @classmethod
    async def update_chat_time(cls, chat_id: ObjectId):
        """更新会话最后更新时间"""
        await AICRUD.update_chat_time(chat_id)

    @classmethod
    async def list_user_chats(cls, user_id: str, skip: int, limit: int):
        """获取用户聊天列表"""
        return await AICRUD.list_user_chats(user_id, skip, limit)

    @classmethod
    async def get_chat_messages(cls, chat_id: ObjectId):
        """获取会话消息列表"""
        return await AICRUD.get_chat_messages(chat_id)

    @classmethod
    async def delete_chat(cls, chat_id: ObjectId, user_id: str):
        """删除会话"""
        return await AICRUD.delete_chat(chat_id, user_id)

# for response in tongyillm.stream("你是谁"):
#     print(response)