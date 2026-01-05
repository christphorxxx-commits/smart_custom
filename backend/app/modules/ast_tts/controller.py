import asyncio
import logging
import time
import os
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Query, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .schema import (
    TTSRequest, ASRRequest, TTSResponse, ASRResponse, 
    ServiceStatus, AudioConfig, WebSocketMessage
)
from .service import AsrService
from .tools.audio_player import AudioPlayer
from .tools.constant import WS_SERVER_URL, WS_HOST, WS_PORT

logger = logging.getLogger(__name__)

# 创建路由实例
ASTTTSRouter = APIRouter(prefix="/ast-tts", tags=["ast-tts"])

# 全局状态管理
class ServiceState:
    def __init__(self):
        self.start_time = time.time()
        self.active_connections = 0
        self.model_loaded = False
        self.asr_available = False
        self.tts_available = False
        self._check_service_status()
    
    def _check_service_status(self):
        """检查服务状态"""
        try:
            # 检查API Key
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if api_key:
                self.asr_available = True
                self.tts_available = True
            
            # 检查模型文件
            from .tools.constant import MODEL_PATH
            if os.path.exists(MODEL_PATH):
                self.model_loaded = True
                
        except Exception as e:
            logger.error(f"服务状态检查失败: {e}")
    
    @property
    def uptime(self) -> float:
        return time.time() - self.start_time

# 全局状态实例
service_state = ServiceState()

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.connection_info: dict = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        service_state.active_connections = len(self.active_connections)
        self.connection_info[websocket] = {
            "connected_at": time.time(),
            "client_ip": websocket.client.host if websocket.client else "unknown"
        }
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            service_state.active_connections = len(self.active_connections)
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for ws in disconnected:
            self.disconnect(ws)

manager = ConnectionManager()

# ==================== HTTP API 端点 ====================

@ASTTTSRouter.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    文字转语音API
    """
    try:
        logger.info(f"收到TTS请求: {request.text[:50]}...")
        
        # 调用TTS服务
        audio_url = await AsrService.getvoice_service(request.text)
        
        return TTSResponse(
            success=True,
            audio_url=audio_url,
            message="TTS转换成功"
        )
        
    except Exception as e:
        logger.error(f"TTS转换失败: {e}")
        return TTSResponse(
            success=False,
            message=f"TTS转换失败: {str(e)}"
        )

@ASTTTSRouter.post("/asr", response_model=ASRResponse)
async def speech_to_text(request: ASRRequest):
    """
    语音转文字API
    """
    try:
        # 确定音频源
        audio_path = request.audio_path or request.audio_url
        if not audio_path:
            raise HTTPException(status_code=400, detail="需要提供音频文件路径或URL")
        
        logger.info(f"收到ASR请求: {audio_path}")
        
        # 调用ASR服务
        text = await AsrService.asr_service(audio_path)
        
        return ASRResponse(
            success=True,
            text=text,
            message="ASR转换成功"
        )
        
    except Exception as e:
        logger.error(f"ASR转换失败: {e}")
        return ASRResponse(
            success=False,
            message=f"ASR转换失败: {str(e)}"
        )

@ASTTTSRouter.post("/asr/upload")
async def upload_audio_for_asr(
    file: UploadFile = File(...),
    language: str = Query("zh", description="识别语言")
):
    """
    上传音频文件进行ASR转换
    """
    try:
        # 保存上传的文件
        file_path = f"/tmp/uploaded_{int(time.time())}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"收到音频上传: {file_path}")
        
        # 进行ASR转换
        text = await AsrService.asr_service(file_path)
        
        # 清理临时文件
        try:
            os.remove(file_path)
        except:
            pass
        
        return ASRResponse(
            success=True,
            text=text,
            message="文件上传并转换成功"
        )
        
    except Exception as e:
        logger.error(f"文件上传ASR转换失败: {e}")
        return ASRResponse(
            success=False,
            message=f"转换失败: {str(e)}"
        )

@ASTTTSRouter.get("/status", response_model=ServiceStatus)
async def get_service_status():
    """
    获取服务状态
    """
    return ServiceStatus(
        status="running" if service_state.asr_available or service_state.tts_available else "degraded",
        asr_available=service_state.asr_available,
        tts_available=service_state.tts_available,
        model_loaded=service_state.model_loaded,
        active_connections=service_state.active_connections,
        uptime=service_state.uptime,
        version="1.0.0"
    )

@ASTTTSRouter.get("/config", response_model=AudioConfig)
async def get_audio_config():
    """
    获取音频配置
    """
    return AudioConfig()

@ASTTTSRouter.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "AST-TTS"
    }

@ASTTTSRouter.get("/voices")
async def get_available_voices():
    """
    获取可用的TTS声音列表
    """
    from .schema import TTSVoiceEnum
    return {
        "voices": [voice.value for voice in TTSVoiceEnum]
    }

# # ==================== WebSocket 端点 ====================
#
# @ASTTTSRouter.websocket("/stream")
# async def audio_stream_handler(websocket: WebSocket):
#     """
#     实时音频流处理WebSocket端点
#     """
#     await manager.connect(websocket)
#
#     # 创建音频播放器
#     audio_player = AudioPlayer()
#
#     try:
#         while True:
#             # 接收客户端消息
#             data = await websocket.receive()
#
#             if "text" in data:
#                 # 处理文本消息，进行TTS
#                 text = data["text"]
#                 logger.info(f"收到TTS请求: {text[:50]}...")
#
#                 # 启动TTS处理
#                 asyncio.create_task(perform_tts_stream(websocket, text, audio_player))
#
#             elif "bytes" in data:
#                 # 处理音频字节数据，进行ASR
#                 audio_data = data["bytes"]
#                 logger.info(f"收到音频数据: {len(audio_data)} bytes")
#
#                 # 保存临时音频文件
#                 temp_path = f"/tmp/stream_{int(time.time())}.wav"
#                 with open(temp_path, "wb") as f:
#                     f.write(audio_data)
#
#                 # 启动ASR处理
#                 asyncio.create_task(perform_asr_stream(websocket, temp_path))
#
#     except WebSocketDisconnect:
#         logger.info("WebSocket连接断开")
#     except Exception as e:
#         logger.error(f"WebSocket处理错误: {e}")
#         await websocket.close(code=1011, reason=f"服务器错误: {str(e)}")
#     finally:
#         manager.disconnect(websocket)
#         audio_player.close()

# @ASTTTSRouter.websocket("/tts")
# async def tts_websocket_handler(websocket: WebSocket):
#     """
#     专门的TTS WebSocket端点
#     """
#     await manager.connect(websocket)
#     audio_player = AudioPlayer()
#
#     try:
#         while True:
#             # 接收文本
#             text = await websocket.receive_text()
#             logger.info(f"收到TTS文本: {text[:50]}...")
#
#             # 执行TTS流式处理
#             await perform_tts_stream(websocket, text, audio_player)
#
#     except WebSocketDisconnect:
#         logger.info("TTS WebSocket连接断开")
#     except Exception as e:
#         logger.error(f"TTS WebSocket错误: {e}")
#         await websocket.close(code=1011, reason=f"TTS处理错误: {str(e)}")
#     finally:
#         manager.disconnect(websocket)
#         audio_player.close()
#
# @ASTTTSRouter.websocket("/asr")
# async def asr_websocket_handler(websocket: WebSocket):
#     """
#     专门的ASR WebSocket端点
#     """
#     await manager.connect(websocket)
#
#     try:
#         while True:
#             # 接收音频数据
#             audio_data = await websocket.receive_bytes()
#             logger.info(f"收到ASR音频: {len(audio_data)} bytes")
#
#             # 保存临时文件
#             temp_path = f"/tmp/asr_{int(time.time())}.wav"
#             with open(temp_path, "wb") as f:
#                 f.write(audio_data)
#
#             # 执行ASR处理
#             text = await AsrService.asr_service(temp_path)
#
#             # 返回识别结果
#             await websocket.send_text(text)
#
#             # 清理临时文件
#             try:
#                 os.remove(temp_path)
#             except:
#                 pass
#
#     except WebSocketDisconnect:
#         logger.info("ASR WebSocket连接断开")
#     except Exception as e:
#         logger.error(f"ASR WebSocket错误: {e}")
#         await websocket.close(code=1011, reason=f"ASR处理错误: {str(e)}")
#     finally:
#         manager.disconnect(websocket)
#
# # ==================== 辅助函数 ====================
#
# async def perform_tts_stream(websocket: WebSocket, text: str, audio_player: AudioPlayer):
#     """
#     执行TTS流式处理
#     """
#     try:
#         # 启动TTS服务
#         await AsrService.tts_service(text)
#
#         # 发送完成信号
#         await websocket.send_text("TTS_COMPLETE")
#
#     except Exception as e:
#         logger.error(f"TTS流式处理失败: {e}")
#         await websocket.send_text(f"TTS_ERROR: {str(e)}")
#
# async def perform_asr_stream(websocket: WebSocket, audio_path: str):
#     """
#     执行ASR流式处理
#     """
#     try:
#         # 执行ASR转换
#         text = await AsrService.asr_service(audio_path)
#
#         # 发送识别结果
#         await websocket.send_text(text)
#
#     except Exception as e:
#         logger.error(f"ASR流式处理失败: {e}")
#         await websocket.send_text(f"ASR_ERROR: {str(e)}")
#     finally:
#         # 清理临时文件
#         try:
#             os.remove(audio_path)
#         except:
#             pass
#
# # ==================== 服务启动函数 ====================
#
# async def start_ast_tts_services():
#     """
#     启动AST-TTS相关服务
#     """
#     logger.info("启动AST-TTS服务...")
#
#     # 这里可以添加启动TTS WebSocket服务器的逻辑
#     # 如果需要单独的WebSocket服务器，可以在这里启动
#
#     logger.info("AST-TTS服务启动完成")

# # 导出路由和状态
# __all__ = ["ASTTTSRouter", "service_state", "start_ast_tts_services"]