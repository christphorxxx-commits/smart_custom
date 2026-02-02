# 文件位置: d:\pycharmWorkspace\smart_custom\backend\app\common\audio_recorder.py

import os
import threading
import wave
from typing import Optional, Callable

import webrtcvad
from pyaudio import PyAudio

from backend.app.common.core.core import logger
from backend.app.constant import AUDIO_FORMAT, AUDIO_CHANNELS, AUDIO_RATE, CHUNK_SIZE


class AudioRecorder:
    """支持VAD的麦克风录音器类"""

    def __init__(self, aggressiveness: int = 2):
        """
        Args:
            aggressiveness: VAD灵敏度 (0-3)，越高越激进
        """
        self.is_running = False
        self.logger = logger
        self.p: Optional[PyAudio] = None
        self.stream = None
        self.audio_frames = []
        self.is_recording = False
        self.recording_thread = None
        #webrtcvad 是基于 Google WebRTC 项目的开源 VAD 算法
        self.vad = webrtcvad.Vad(aggressiveness)
        self._vad_callback: Optional[Callable[[bool], None]] = None
        self._init_audio()

    def set_vad_callback(self, callback: Callable[[bool], None]):
        """
        设置VAD回调函数

        Args:
            callback: 回调函数，参数为 bool (True=检测到语音, False=语音结束)
        """
        self._vad_callback = callback

    def _init_audio(self):
        """初始化音频设备"""
        try:
            self.p = PyAudio()
            self.logger.info("麦克风录音器初始化成功（支持VAD）")
        except Exception as e:
            self.logger.error(f"麦克风录音器初始化失败: {e}")
            raise

    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            self.logger.warning("已经在录音中")
            return

        self.audio_frames = []
        self.is_recording = True

        self.stream = self.p.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=AUDIO_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
            start=False
        )
        self.stream.start_stream()

        self.recording_thread = threading.Thread(target=self._record_worker, daemon=True)
        self.recording_thread.start()
        self.logger.info("开始录音（VAD已启用）")

    def _record_worker(self):
        """录音工作线程（带VAD检测）"""
        try:
            speech_detected = False
            silence_frames = 0
            max_silence_frames = 30  # 约1秒的静音认为语音结束

            while self.is_recording:
                try:
                    data = self.stream.read(CHUNK_SIZE)
                    self.audio_frames.append(data)

                    # VAD检测
                    is_speech = self.vad.is_speech(data, AUDIO_RATE)

                    if is_speech:
                        speech_detected = True
                        silence_frames = 0
                        if self._vad_callback:
                            self._vad_callback(True)  # 检测到语音
                    else:
                        silence_frames += 1
                        # 连续静音则认为语音结束
                        if speech_detected and silence_frames > max_silence_frames:
                            if self._vad_callback:
                                self._vad_callback(False)  # 语音结束
                            speech_detected = False

                except Exception as e:
                    self.logger.error(f"录音时出错: {e}")
                    break

        except Exception as e:
            self.logger.error(f"录音工作线程出错: {e}")

    def stop_recording(self) -> Optional[str]:
        """停止录音并保存为文件"""
        if not self.is_recording:
            self.logger.warning("没有在录音")
            return None

        self.is_recording = False

        if self.recording_thread:
            self.recording_thread.join(timeout=2)

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                self.logger.error(f"关闭音频流时出错: {e}")

        file_path = self._save_to_wave_file()
        self.logger.info(f"录音已保存到: {file_path}")
        return file_path

    def _save_to_wave_file(self, output_path: Optional[str] = None) -> str:
        """保存录音数据为WAV文件"""
        if output_path is None:
            output_dir = "recordings"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = len(os.listdir(output_dir)) + 1
            output_path = os.path.join(output_dir, f"recording_{timestamp}.wav")

        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(AUDIO_CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(AUDIO_FORMAT))
            wf.setframerate(AUDIO_RATE)
            wf.writeframes(b''.join(self.audio_frames))

        return output_path

    def get_audio_data(self) -> bytes:
        """获取录音的音频数据（不保存文件）"""
        return b''.join(self.audio_frames)

    def close(self):
        """关闭录音器"""
        if self.is_recording:
            self.stop_recording()

        if self.p:
            self.p.terminate()

        self.logger.info("麦克风录音器已关闭")

