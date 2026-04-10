from collections.abc import AsyncIterable

from bson import ObjectId
from fastapi.sse import ServerSentEvent

from backend.app.common.core.core import tongyillm
from backend.app.common.core.logger import log
from backend.app.modules.api.ai.crud import AICRUD
from backend.app.modules.api.ai.schema import ChatQuerySchema
from .model import Chat, ChatItem


class AIService:
    """AI聊天服务层"""

    @classmethod
    def chat_service(cls, query: ChatQuerySchema):
        """
        处理聊天查询（带记忆功能，加载完整聊天历史）
        :param query: 聊天查询模型
        :return: 生成器，每次返回一个聊天响应
        """
        try:
            from langchain_core.messages import HumanMessage, AIMessage
            # 构建完整消息列表（包含历史记忆）
            messages = []

            # 如果有chat_id，加载历史消息作为记忆
            if query.chat_id:
                # 需要异步获取，但这是同步方法，直接只处理当前消息
                # 同步方法一般不用，保持向后兼容
                pass

            # 添加当前用户最新消息
            messages.append(HumanMessage(content=query.message))

            for response in tongyillm.stream(messages):
                yield response.content

        except Exception as e:
            log.error(f"AI对话出现问题: {e}", exc_info=True)

    @classmethod
    async def chat_stream_generator(cls, query: ChatQuerySchema, chat_id: ObjectId):
        """
        异步流式生成，保存AI回复到MongoDB后完成（带记忆功能，加载完整聊天历史）
        :param query: 聊天查询
        :param chat_id: 会话ID（已经在controller创建好）
        :yield: 每个token字节
        """
        from langchain_core.messages import HumanMessage, AIMessage

        # 构建完整消息列表（包含历史记忆）
        messages = []

        # 加载历史消息作为记忆
        history = await cls.get_chat_messages(chat_id)
        # 将历史消息转换为langchain消息格式
        for item in history:
            if item.role == "user":
                messages.append(HumanMessage(content=item.content))
            elif item.role == "assistant":
                messages.append(AIMessage(content=item.content))

        # 添加当前用户最新消息
        messages.append(HumanMessage(content=query.message))
        full_response = ""

        try:
            for response in tongyillm.stream(messages):
                if response.content:
                    full_response += response.content
                    yield response.content.encode('utf-8')

            # 流式完成，保存完整AI回复
            if full_response:
                await cls.save_message(chat_id, "assistant", full_response)
                await cls.update_chat_time(chat_id)

        except Exception as e:
            log.error(f"AI流式生成出错: {e}", exc_info=True)
            error_msg = f"抱歉，处理您的请求时出现了错误：{str(e)}"
            yield error_msg.encode("utf-8")

    @classmethod
    async def chat_service_sse(cls, query: ChatQuerySchema) -> AsyncIterable[ServerSentEvent]:
        """
        异步流式生成（带记忆功能，加载完整聊天历史）
        :param query: 聊天查询
        :param chat_id: 会话ID（已经在controller创建好）
        """
        from langchain_core.messages import HumanMessage, AIMessage

        # 构建完整消息列表（包含历史记忆）
        messages = []

        # 如果有chat_id，加载历史消息作为记忆
        if query.chat_id:
            history = await cls.get_chat_messages(ObjectId(query.chat_id))
            # 将历史消息转换为langchain消息格式
            for item in history:
                if item.role == "user":
                    messages.append(HumanMessage(content=item.content))
                elif item.role == "assistant":
                    messages.append(AIMessage(content=item.content))

        # 添加当前用户最新消息
        messages.append(HumanMessage(content=query.message))
        full_response = ""

        try:
            async for response in tongyillm.astream(messages):
                if response.content:
                    full_response += response.content
                    yield ServerSentEvent(data=response.content,event="token")
            # yield ServerSentEvent(raw_data="[DONE]", event="done")
            # 流式完成，保存完整AI回复
            if full_response:
                await cls.save_message(ObjectId(query.chat_id), "assistant", full_response)
                await cls.update_chat_time(ObjectId(query.chat_id))

        except Exception as e:
            log.error(f"AI流式生成出错: {e}", exc_info=True)
            error_msg = f"抱歉，处理您的请求时出现了错误：{str(e)}"
            yield ServerSentEvent(data=error_msg, event="error")


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