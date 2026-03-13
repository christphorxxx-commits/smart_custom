import logging
import os
import uuid
from typing import AsyncGenerator, Any

from backend.app.common.core.core import tongyillm
from backend.app.modules.ai.schema import ChatQuerySchema

# 配置日志
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

for response in tongyillm.stream("你是谁"):
    print(response)