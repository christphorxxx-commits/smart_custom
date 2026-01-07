from fastapi import APIRouter
from backend.app.modules.ai.service import AIService
from backend.app.modules.ai.schema import ChatRequest, ChatResponse

AIRouter = APIRouter(prefix="/ai", tags=["ai"])


@AIRouter.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI聊天接口

    :param request: 聊天请求参数
    :return: 聊天响应结果
    """
    result = await AIService.chat_service(
        text=request.text,
        session_id=request.session_id
    )

    return ChatResponse(
        success=result["success"],
        text=result["text"],
        session_id=result["session_id"],
        message=result.get("message"),
        context=result.get("context")
    )


