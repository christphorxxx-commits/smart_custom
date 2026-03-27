from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.common.response import StreamResponse
from backend.app.common.core.dependencies import db_getter
from backend.app.modules.api.ai.service import AIService
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.common.core.logger import log


AIRouter = APIRouter(prefix="/ai", tags=["ai"])


from backend.app.common.core.dependencies import get_current_user
from backend.app.modules.module_system.user.model import UserModel

@AIRouter.post("/chat", summary="智能对话", description="与智能助手进行对话")
async def chat(
        query: ChatQuerySchema,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(db_getter),
) -> StreamingResponse:
    """
    智能对话接口

    :param query: 聊天查询模型
    :param current_user: 当前登录用户
    :param db: 数据库会话
    :return: 
    -StreamingResponse： 流式响应，每次返回一个聊天响应
    """
    # 创建AuthSchema实例，并设置用户信息
    auth = AuthSchema(db=db, user=current_user)
    
    user_name = auth.user.username if auth.user else "未知用户"
    log.info(f"用户 {user_name} 发起智能对话: {query.message[:50]}...")

    async def generate_response():
        try:
            for chunk in AIService.chat_service(query=query):
                #确保返回的是字节串
                if chunk:
                    yield chunk.encode('utf-8') if isinstance(chunk, str) else chunk
        except Exception as e:
            log.error(f"流式响应出错：{str(e)}")
            yield f"抱歉，处理您的请求时出现了错误：{str(e)}".encode("utf-8")


    return StreamResponse(generate_response(), media_type="text/plain; charset=utf-8")


# for chunk in AIService.chat_service(query=ChatQuerySchema(message="你是谁",session_id="0",context=None)):
#     if chunk:
#         print(chunk.content)



