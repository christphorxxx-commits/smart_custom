from fastapi import WebSocket,WebSocketDisconnect
from backend.app.modules.tts.service import AudioService
from backend.app.common.core import logger,voice,manager,llm
from fastapi import APIRouter


#初始化服务实例
audio_service = AudioService()

TTSRouter = APIRouter(prefix="/tts", tags=["TTS"])

# @TTSRouter.websocket("/tts")
# async def tts_websocket_audio(websocket: WebSocket):
#     path = "/tts"
#     try:
#         #1.建立WebSocket链接（控制器负责连接管理）
#         await manager.connect(websocket,path)
#
#         #循环接受客户端消息
#         while True:
#             #接受客户端文本（控制器负责IO操作）
#             data = await websocket.receive_text()
#             try:
#                 #3.调用服务层处理核心业务（控制器不写业务逻辑）
#                 audio_service.synthesize_and_play_audio(text=data, voice_module=voice)
#
#                 # 可选：给客户端返回处理成功的提示
#                 await websocket.send_text(f"文本处理完成，已开始播放音频（文本长度：{len(data)}字）")
#             except ValueError as e:
#                 # 捕获业务异常，返回友好提示
#                 logger.error(f"业务处理失败：{str(e)}")
#                 await websocket.send_text(f"错误：{str(e)}")
#             except Exception as e:
#                 # 捕获未知异常，返回通用提示
#                 logger.error(f"音频合成/播放异常：{str(e)}", exc_info=True)
#                 await websocket.send_text(f"服务端错误：{str(e)}")
#     except WebSocketDisconnect:
#         # 4. 断开连接（控制器负责清理）
#         manager.disconnect(websocket, path)
#         logger.info("客户端主动断开 WebSocket 连接")
#     except Exception as e:
#         # 全局异常捕获
#         logger.error(f"WebSocket 连接异常：{str(e)}", exc_info=True)
#         manager.disconnect(websocket, path)

@TTSRouter.websocket("/tts")
async def tts_ai_websocket(websocket: WebSocket):
    path = "/tts"
    try:
        #1.建立WebSocket链接（控制器负责连接管理）
        await manager.connect(websocket,path)

        #循环接受客户端消息
        while True:
            #接受客户端文本（控制器负责IO操作）
            data = await websocket.receive_text()

            #使用llm传入客户端文本得到回复
            response = llm.invoke(data)

            #打印出llm的回复
            print(response)

            try:
                #3.调用服务层处理核心业务（控制器不写业务逻辑）
                audio_service.synthesize_and_play_audio(text=response.text, voice_module=voice)

                # 可选：给客户端返回处理成功的提示
                await websocket.send_text(f"文本处理完成，已开始播放音频）")
            except ValueError as e:
                # 捕获业务异常，返回友好提示
                logger.error(f"业务处理失败：{str(e)}")
                await websocket.send_text(f"错误：{str(e)}")
            except Exception as e:
                # 捕获未知异常，返回通用提示
                logger.error(f"音频合成/播放异常：{str(e)}", exc_info=True)
                await websocket.send_text(f"服务端错误：{str(e)}")
    except WebSocketDisconnect:
        # 4. 断开连接（控制器负责清理）
        manager.disconnect(websocket, path)
        logger.info("客户端主动断开 WebSocket 连接")
    except Exception as e:
        # 全局异常捕获
        logger.error(f"WebSocket 连接异常：{str(e)}", exc_info=True)
        manager.disconnect(websocket, path)
