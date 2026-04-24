# app/tts/service.py
import asyncio
import queue
import threading
from typing import AsyncGenerator, Optional
from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback, AudioFormat
import dashscope

from .schema import TTSError


class TTSService:
    def __init__(self):
        self.active_sessions = {}  # session_id -> synthesizer

    async def synthesize_stream(
            self,
            session_id: str,
            text: str,
            model: str = "cosyvoice-v3-flash",
            voice: str = "longanyang"
    ) -> AsyncGenerator[bytes | TTSError, None]:
        """
        流式合成语音，返回音频字节流或错误
        """
        audio_queue = queue.Queue()
        error_event = threading.Event()
        error_msg = [None]

        class InternalCallback(ResultCallback):
            def on_data(self, data: bytes):
                audio_queue.put(data)

            def on_error(self, message: str):
                error_msg[0] = TTSError(error=message)
                error_event.set()

            def on_complete(self):
                audio_queue.put(None)  # 结束标志

            def on_close(self):
                if not error_event.is_set():
                    audio_queue.put(None)

        callback = InternalCallback()

        # 映射 format
        audio_format = AudioFormat.PCM_22050HZ_MONO_16BIT  # CosyVoice 固定 22050Hz

        synthesizer = SpeechSynthesizer(
            model=model,
            voice=voice,
            format=audio_format,
            callback=callback
        )

        self.active_sessions[session_id] = synthesizer

        try:
            # 启动流式合成
            synthesizer.streaming_call(text)
            synthesizer.streaming_complete()

            while True:
                if error_event.is_set():
                    yield error_msg[0]
                    break

                try:
                    item = audio_queue.get(timeout=0.1)
                    if item is None:
                        break
                    yield item
                except queue.Empty:
                    continue
        finally:
            synthesizer.close()
            self.active_sessions.pop(session_id, None)

    def stop_session(self, session_id: str):
        """停止 TTS 会话"""
        synthesizer = self.active_sessions.pop(session_id, None)
        if synthesizer:
            synthesizer.close()