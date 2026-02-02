# 文件位置: d:\pycharmWorkspace\smart_custom\backend\app\modules\asr\interaction_controller.py

import asyncio
import logging
from typing import Optional, Callable
from enum import Enum
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.common.audio_player import AudioPlayer
from backend.app.common.audio_recorder import AudioRecorder
from backend.app.modules.asr.service import ASRService

logger = logging.getLogger(__name__)


class InteractionState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    RECORDING = "recording"


InteractionRouter = APIRouter(prefix="/interaction", tags=["Interaction"])


class InteractionController:
    """交互控制器 - 管理录音/播放状态，支持打断"""

    def __init__(self):
        self.state = InteractionState.IDLE
        self.audio_player = None
        self.audio_recorder = None
        self._setup_devices()

    def _setup_devices(self):
        """初始化音频设备"""
        try:
            self.audio_player = AudioPlayer()
            self.audio_recorder = AudioRecorder()
            self.audio_recorder.set_vad_callback(self._on_speech_detected)
            logger.info("音频设备初始化成功")
        except Exception as e:
            logger.error(f"音频设备初始化失败: {e}")
            raise

    def _on_speech_detected(self, is_speech: bool):
        """
        VAD回调函数 - 检测到用户说话时调用

        Args:
            is_speech: True=检测到语音, False=语音结束
        """
        if is_speech and self.state == InteractionState.PLAYING:
            logger.info("检测到用户打断，停止当前播放")
            self._interrupt_playback()

    def _interrupt_playback(self):
        """打断当前播放"""
        if self.audio_player:
            self.audio_player.stop()
        self.state = InteractionState.IDLE

    async def start_recording(self):
        """开始录音（自动打断当前播放）"""
        # 如果正在播放，先打断
        if self.state == InteractionState.PLAYING:
            self._interrupt_playback()

        self.state = InteractionState.RECORDING
        self.audio_recorder.start_recording()
        logger.info("开始录音（可能打断了之前的播放）")

    async def stop_recording(self) -> bytes:
        """停止录音，返回音频数据"""
        if self.state != InteractionState.RECORDING:
            raise RuntimeError("当前没有在录音")

        self.audio_recorder.stop_recording()
        self.state = InteractionState.IDLE

        # 返回音频数据用于识别
        audio_data = self.audio_recorder.get_audio_data()
        return audio_data

    async def play_audio(self, audio_data: bytes):
        """播放音频"""
        if self.state == InteractionState.RECORDING:
            logger.warning("当前正在录音，无法播放")
            return

        self.state = InteractionState.PLAYING

        # 模拟流式播放（实际实现需要TTS服务支持流式输出）
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            self.audio_player.add_audio(chunk)

            # 检查是否需要打断
            if self.state != InteractionState.PLAYING:
                logger.info("播放被中断")
                break

        if self.state == InteractionState.PLAYING:
            self.state = InteractionState.IDLE

    def get_state(self) -> str:
        """获取当前状态"""
        return self.state.value


# 全局控制器实例
controller = InteractionController()


class InteractionResponse(BaseModel):
    success: bool
    state: str
    text: Optional[str] = None
    message: str


@InteractionRouter.post("/start-recording")
async def start_recording():
    """开始录音（会打断当前播放）"""
    try:
        await controller.start_recording()
        return {"success": True, "state": "recording", "message": "开始录音"}
    except Exception as e:
        logger.error(f"开始录音失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@InteractionRouter.post("/stop-recording", response_model=InteractionResponse)
async def stop_recording():
    """停止录音并进行识别"""
    try:
        audio_data = await controller.stop_recording()

        # 保存临时文件用于ASR识别
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        # 调用ASR服务
        text = await ASRService.asr_service(temp_path)

        # 清理临时文件
        import os
        os.unlink(temp_path)

        return InteractionResponse(
            success=True,
            state="idle",
            text=text,
            message="录音和识别完成"
        )
    except Exception as e:
        logger.error(f"停止录音失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@InteractionRouter.get("/state")
async def get_state():
    """获取当前交互状态"""
    return {"state": controller.get_state()}


# # 示例：完整的打断流程演示
# @InteractionRouter.post("/demo-interrupt")
# async def demo_interrupt():
#     """
#     演示打断功能流程：
#     1. 开始播放模拟音频
#     2. 模拟用户打断（实际中通过麦克风VAD检测）
#     """
#     try:
#         # 模拟开始播放
#         await controller.start_playing_demo()
#
#         # 模拟在播放过程中检测到打断
#         # 实际应用中，VAD回调会自动调用 _interrupt_playback()
#         await asyncio.sleep(1)  # 模拟播放1秒后被打断
#
#         # 检查状态
#         if controller.get_state() == "idle":
#             return {
#                 "success": True,
#                 "message": "成功检测到打断并停止了播放",
#                 "state": "idle"
#             }
#
#         return {
#             "success": True,
#             "message": "播放正常完成",
#             "state": "completed"
#         }
#     except Exception as e:
#         logger.error(f"演示失败: {e}")
#         raise HTTPException(status_code=500, detail=str(e))