from typing import Union

from bson import ObjectId
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse

from backend.app.common.constant import RET
from backend.app.common.core.dependencies import db_getter
from backend.app.common.core.logger import log
from backend.app.common.response import StreamResponse
from backend.app.modules.api.ai.schema import ChatListResponse, ChatListResponseItem, ChatMessageListResponse, \
    ChatMessageResponseItem, BasicResponse
from backend.app.modules.api.ai.schema import ChatQuerySchema
from backend.app.modules.api.ai.service import AIService
from backend.app.modules.module_system.auth.schema import AuthSchema

AIRouter = APIRouter(prefix="/ai", tags=["ai"])

from backend.app.common.core.dependencies import get_current_user
from backend.app.modules.module_system.user.model import UserModel


# @AIRouter.post("/chat", summary="智能对话", description="与智能助手进行对话")
# async def chat(
#         query: ChatQuerySchema,
#         current_user: UserModel = Depends(get_current_user),
#         db: AsyncSession = Depends(db_getter),
# ) -> StreamingResponse:
#     """
#     智能对话接口
#
#     :param query: 聊天查询模型
#     :param current_user: 当前登录用户
#     :param db: 数据库会话
#     :return:
#     -StreamingResponse： 流式响应，每次返回一个聊天响应
#     """
#     # 创建AuthSchema实例，并设置用户信息
#     auth = AuthSchema(db=db, user=current_user)
#
#     user_name = auth.user.username if auth.user else "未知用户"
#     log.info(f"用户 {user_name} 发起智能对话: {query.message[:50]}...")
#
#     # 获取或创建聊天会话，并保存用户消息
#     chat = await AIService.get_or_create_chat(
#         chat_id=query.chat_id,
#         user_id=str(current_user.id),
#         first_message=query.message
#     )
#     # 保存用户提问
#     await AIService.save_message(chat.id, "user", query.message)
#     # 更新会话最后更新时间（AI响应失败时依然保持更新，保证聊天列表排序正确）
#     await AIService.update_chat_time(chat.id)
#
#     # 新方式：直接调用service的异步生成器
#     return StreamResponse(
#         AIService.chat_stream_generator(query, chat.id),
#         media_type="text/plain; charset=utf-8"
#     )

    # ========== 原代码保留（已注释） ==========
    # async def generate_response():
    #     try:
    #         full_response = ""
    #         # 流式生成并返回给前端，同时累积完整响应
    #         for chunk in AIService.chat_service(query=query):
    #             if chunk:
    #                 full_response += chunk
    #                 yield chunk.encode('utf-8') if isinstance(chunk, str) else chunk
    #
    #         # 流式输出完成后，保存AI完整回复到MongoDB
    #         if full_response:
    #             await AIService.save_message(chat.id, "assistant", full_response)
    #             await AIService.update_chat_time(chat.id)
    #
    #     except Exception as e:
    #         log.error(f"流式响应出错：{str(e)}", exc_info=True)
    #         error_msg = f"抱歉，处理您的请求时出现了错误：{str(e)}"
    #         yield error_msg.encode("utf-8")
    #
    # return StreamResponse(generate_response(), media_type="text/plain; charset=utf-8")


@AIRouter.post("/chat", summary="智能对话(SSE)", description="与智能助手进行对话，服务器发送事件版本")
async def chat_sse(
        query: ChatQuerySchema,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(db_getter),
) -> EventSourceResponse:
    """
    智能对话接口(SSE 流式响应)

    :param query: 聊天查询模型
    :param current_user: 当前登录用户
    :param db: 数据库会话
    :return: SSE 事件流
    """
    # 创建AuthSchema实例，并设置用户信息
    auth = AuthSchema(db=db, user=current_user)

    user_name = auth.user.username if auth.user else "未知用户"
    log.info(f"用户 {user_name} 发起智能对话(SSE): {query.message[:50]}...")

    # 获取或创建聊天会话，并保存用户消息
    chat = await AIService.get_or_create_chat(
        chat_id=query.chat_id,
        user_id=str(current_user.id),
        first_message=query.message
    )
    query.chat_id = chat.id
    # 保存用户提问
    await AIService.save_message(chat.id, "user", query.message)
    # 更新会话最后更新时间（AI响应失败时依然保持更新，保证聊天列表排序正确）
    await AIService.update_chat_time(chat.id)

    # 返回EventSourceResponse包装异步生成器
    return EventSourceResponse(
        AIService.chat_service_sse(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )




# ============ 额外接口：获取历史对话 ============
@AIRouter.get("/list", summary="获取用户聊天列表", response_model=ChatListResponse)
async def list_chats(
        current_user: UserModel = Depends(get_current_user),
        skip: int = 0,
        limit: int = 20
) -> ChatListResponse:
    """获取当前用户的所有聊天会话列表"""
    chats = await AIService.list_user_chats(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )

    data = [
        ChatListResponseItem(
            id=str(c.id),
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at
        ) for c in chats
    ]

    return ChatListResponse(
        success=True,
        data=data,
        total=len(chats)
    )


@AIRouter.get("/{chat_id}/messages", summary="获取会话的消息历史")
async def get_chat_messages(
        chat_id: str,
        current_user: UserModel = Depends(get_current_user),
) -> Union[ChatMessageListResponse, BasicResponse]:
    """获取指定会话的所有消息记录"""
    try:
        chat = await AIService.get_or_create_chat(
            chat_id=chat_id,
            user_id=str(current_user.id),
            first_message=""
        )
        if not chat or chat.is_deleted or str(chat.user_id) != str(current_user.id):
            return BasicResponse(success=False, msg="会话不存在或无权限",code=RET.ERROR.code)

        messages = await AIService.get_chat_messages(chat.id)

        data = [
            ChatMessageResponseItem(
                role=m.role,
                content=m.content,
                created_at=m.created_at
            ) for m in messages
        ]

        return ChatMessageListResponse(
            success=True,
            title=chat.title,
            data=data
        )
    except Exception as e:
        return BasicResponse(success=False, msg=str(e),code=RET.ERROR.code)


@AIRouter.delete("/{chat_id}", summary="删除聊天会话", response_model=BasicResponse)
async def delete_chat(
        chat_id: str,
        current_user: UserModel = Depends(get_current_user),
) -> BasicResponse:
    """软删除聊天会话"""
    success, msg = await AIService.delete_chat(
        chat_id=ObjectId(chat_id),
        user_id=str(current_user.id)
    )
    return BasicResponse(success=success, msg=msg,code=RET.OK.code)
