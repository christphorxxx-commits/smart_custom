import logging
import os
import uuid
from backend.app.common.core import llm

import dashscope

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AIService:
    """AI聊天服务层"""

    @classmethod
    async def chat_service(cls, text: str, session_id: str = None) -> dict:
        """
        AI聊天服务
        
        :param text: 用户输入文本
        :param session_id: 会话ID
        :return: 聊天响应结果
        """
        try:
            if not text:
                raise ValueError("输入文本不能为空")
                
            # 生成会话ID（如果没有提供）
            if not session_id:
                session_id = str(uuid.uuid4())
                
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("DASHSCOPE_API_KEY 环境变量未配置")

            #llm输出得到response
            #TODO llm提升为RAG应用
            response = llm.invoke(text)

            return {
                "success": True,
                "text": response.text,
                "session_id": session_id
            }
        except Exception as e:
            logger.error(f"AI聊天失败: {e}", exc_info=True)
            return {
                "success": False,
                "text": "",
                "session_id": session_id,
                "message": str(e)
            }
