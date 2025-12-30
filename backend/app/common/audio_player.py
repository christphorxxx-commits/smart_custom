# -*- coding: utf-8 -*-
"""
音频播放模块
负责音频数据的实时播放，避免频繁初始化音频设备
"""

import queue
import threading
import logging
import pyaudio
from backend.app.constant import AUDIO_FORMAT, AUDIO_CHANNELS, AUDIO_RATE,CHUNK_SIZE,AUDIO_QUEUE_SIZE


def setup_global_logging():
    """配置全局日志，确保能看到所有级别日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # 输出到控制台
        ]
    )

# 初始化全局日志
setup_global_logging()

class AudioPlayer:
    """音频播放器类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)  # 使用全局配置的logger
        self.p = None
        self.stream = None
        self.audio_queue = queue.Queue(maxsize=AUDIO_QUEUE_SIZE)
        self.playing_thread = None
        self.is_running = False
        self.played_chunks = 0
        self.dropped_chunks = 0
        self._init_audio()


    def _init_audio(self):
        """初始化音频设备"""
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_RATE,
                output=True,
                frames_per_buffer=CHUNK_SIZE,
                start=False  # 不立即开始播放
            )
            self.is_running = True
            self.playing_thread = threading.Thread(target=self._play_worker, daemon=True)
            self.playing_thread.start()
            self.logger.info("音频播放器初始化成功")
            self.logger.info(f"音频配置: 格式={AUDIO_FORMAT}, 通道={AUDIO_CHANNELS}, 采样率={AUDIO_RATE}")
        except Exception as e:
            self.logger.error(f"音频播放器初始化失败: {e}")
            raise

    def _play_worker(self):
        """后台播放工作线程"""
        self.logger.info("音频播放工作线程已启动")

        try:
            self.stream.start_stream()

            while self.is_running:
                try:
                    # 从队列获取音频数据，设置超时避免线程阻塞
                    audio_data = self.audio_queue.get(timeout=1)
                    self._play_chunk(audio_data)
                    self.played_chunks += 1

                except queue.Empty:
                    # 队列为空时继续循环
                    continue
                except Exception as e:
                    self.logger.error(f"播放音频时出错: {e}")

        except Exception as e:
            self.logger.error(f"播放工作线程出错: {e}")
        finally:
            self.logger.info(f"播放工作线程结束，总播放片段: {self.played_chunks}, 丢弃片段: {self.dropped_chunks}")

    def _play_chunk(self, audio_data):
        """播放单个音频片段"""
        try:
            if not self.stream or not self.stream.is_active():
                self.logger.warning("音频流不活跃，重新初始化")
                self._init_stream()

            self.stream.write(audio_data)

        except Exception as e:
            self.logger.error(f"播放音频片段失败: {e}")

    def _init_stream(self):
        """重新初始化音频流"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

            self.stream = self.p.open(
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_RATE,
                output=True,
                frames_per_buffer=CHUNK_SIZE,
                start=True
            )
            self.logger.info("音频流重新初始化成功")

        except Exception as e:
            self.logger.error(f"音频流重新初始化失败: {e}")
            raise

    def add_audio(self, audio_data):
        """
        添加音频到播放队列

        Args:
            audio_data (bytes): 音频数据

        Returns:
            bool: 是否成功添加到队列
        """
        try:
            # 非阻塞添加，超时时间设为0.01秒
            self.audio_queue.put(audio_data, timeout=0.01)
            return True

        except queue.Full:
            self.dropped_chunks += 1
            if self.dropped_chunks % 10 == 1:  # 每10个丢弃片段记录一次
                self.logger.warning(f"音频队列已满，丢弃音频片段 (总计丢弃: {self.dropped_chunks})")
            return False
        except Exception as e:
            self.logger.error(f"添加音频到队列失败: {e}")
            return False

    def get_queue_size(self):
        """获取当前队列大小"""
        return self.audio_queue.qsize()

    def get_stats(self):
        """获取播放统计信息"""
        return {
            "played_chunks": self.played_chunks,
            "dropped_chunks": self.dropped_chunks,
            "queue_size": self.get_queue_size(),
            "is_running": self.is_running
        }

    def close(self):
        """关闭音频播放器"""
        self.logger.info("开始关闭音频播放器...")
        self.is_running = False

        # 等待播放工作线程结束
        if self.playing_thread and self.playing_thread.is_alive():
            self.playing_thread.join(timeout=2)

        # 清理音频流
        try:
            if self.stream:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
        except Exception as e:
            self.logger.error(f"关闭音频流时出错: {e}")

        # 清理PyAudio
        try:
            if self.p:
                self.p.terminate()
        except Exception as e:
            self.logger.error(f"终止PyAudio时出错: {e}")

        self.logger.info("音频播放器已关闭")

    def __enter__(self):
        """支持with语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句的清理"""
        self.close()