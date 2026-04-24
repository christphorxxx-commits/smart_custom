import asyncio
import os

import whisper
from dotenv import load_dotenv
load_dotenv()
import dashscope

from backend.app.common.core.logger import log


# app/asr/service.py
import asyncio
import queue
import threading
from typing import AsyncGenerator, Optional
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
import dashscope

from .schema import ASRResult, ASRError


class ASRService:
    def __init__(self):
        self.active_sessions = {}  # session_id -> Recognition 实例

    async def start_streaming_asr(
        self,
        session_id: str,
        model: str = "fun-asr-realtime",
        sample_rate: int = 16000,
        audio_format: str = "pcm"
    ) -> AsyncGenerator[ASRResult | ASRError, None]:
        """
        启动一个流式 ASR 会话，返回异步生成器用于推送结果
        """
        result_queue = queue.Queue()
        error_event = threading.Event()
        error_msg = [None]

        class InternalCallback(RecognitionCallback):
            def on_event(self, result: RecognitionResult):
                sentence = result.get_sentence()
                if 'text' in sentence:
                    text = sentence['text']
                    is_final = RecognitionResult.is_sentence_end(sentence)
                    res = ASRResult(
                        text=text,
                        is_final=is_final,
                        request_id=result.get_request_id(),
                        timestamp=asyncio.get_event_loop().time()
                    )
                    result_queue.put(res)

            def on_error(self, message):
                error_msg[0] = ASRError(error=message.message)
                error_event.set()

            def on_close(self):
                result_queue.put(None)  # 结束信号

        callback = InternalCallback()
        recognition = Recognition(
            model=model,
            format=audio_format,
            sample_rate=sample_rate,
            callback=callback
        )

        recognition.start()
        self.active_sessions[session_id] = recognition

        try:
            while True:
                if error_event.is_set():
                    yield error_msg[0]
                    break

                try:
                    # 非阻塞获取结果（超时 0.1s）
                    item = result_queue.get(timeout=0.1)
                    if item is None:
                        break
                    yield item
                except queue.Empty:
                    continue
        finally:
            recognition.stop()
            self.active_sessions.pop(session_id, None)

    def send_audio_frame(self, session_id: str, audio_data: bytes):
        """向指定会话发送音频帧"""
        recognition = self.active_sessions.get(session_id)
        if recognition:
            recognition.send_audio_frame(audio_data)

    def stop_session(self, session_id: str):
        """停止会话"""
        recognition = self.active_sessions.pop(session_id, None)
        if recognition:
            recognition.stop()