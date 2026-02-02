from enum import Enum
from backend.app.common.audio_player import AudioPlayer
from backend.app.common.audio_recorder import AudioRecorder
from backend.app.common.core.core import logger

import whisper
from dotenv import load_dotenv
load_dotenv()

class ASRTTSState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    RECORDING = "recording"



class ASRTTSService:

    def __init__(self):
        self.state = ASRTTSState.IDLE
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
        if is_speech and self.state == ASRTTSState.PLAYING:
            logger.info("检测到用户打断，停止当前播放")
            self._interrupt_playback()

    def _interrupt_playback(self):
        """打断当前播放"""
        if self.audio_player:
            self.audio_player.stop()
        self.state = ASRTTSState.IDLE


    def _init_whisper_model(self):
        """初始化Whisper模型（仅在首次使用时加载）"""

        if self._whisper_model is None:
            logger.info(f"加载Whisper模型: {self._model_config['model_name']}，设备: {self._model_config['device']}")
            self._whisper_model = whisper.load_model(
                self._model_config['model_name'],
                device=self._model_config['device']
            )

    async def start_recording(self):
        """
        开始录音，自动打断当前播放
        :return:
        """

        if self.state == ASRTTSState.PLAYING:
            self._interrupt_playback()

        #设置当前状态为录音中
        self.state = ASRTTSState.RECORDING

        #启动audio_recorder开始录音
        self.audio_recorder.start_recording()

        logger.info("开始录音")

    async def stop_recording(self) -> bytes:
        """
        停止录音返回数据以供识别
        :return: audio_data
        """
        #1.判断当前麦克风有没有在录音
        if self.state != ASRTTSState.RECORDING:
            logger.info("当前没有录音")

        #设置当前服务状态为空
        self.state = ASRTTSState.IDLE

        #停止录音并保存录音到一个位置
        self.audio_recorder.stop_recording()

        audio_data = self.audio_recorder.get_audio_data()

        return audio_data


    # async def ASR
    async def play_audio(self,audio_data:bytes):

        if self.state == ASRTTSState.RECORDING:
            logger.warning("当前正在录音，不能播放")
            return
        self.state = ASRTTSState.PLAYING






