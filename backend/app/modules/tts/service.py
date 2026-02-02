from backend.app.common.audio_player import AudioPlayer
from backend.app.common.core.core import logger


class AudioService:
    def __init__(self):
        # 初始化音频播放器（每个服务实例一个播放器，可根据需求调整为单例）
        self.player = AudioPlayer()

    @classmethod
    def synthesize_and_play_audio(self, text: str, voice_module) -> None:
        """
        核心业务：合成语音并播放
        :param text: 用户输入的文本
        :param voice_module: 语音合成模块（如你的 voice 对象）
        :raise ValueError: 文本为空/合成失败时抛出异常
        """
        # 1. 基础业务校验（服务层负责）
        if not text or len(text.strip()) == 0:
            raise ValueError("合成文本不能为空")

        logger.info(f"开始处理文字：{text[:20]}...（总长度：{len(text)}字）")

        # 2. 实时合成音频并添加到播放器
        # audio_chunks = voice_module.synthesize(text)
        for chunk in voice_module.synthesize(text):
            if hasattr(chunk, "audio_int16_bytes") and chunk.audio_int16_bytes:
                self.player.add_audio(chunk.audio_int16_bytes)
                logger.info(f"添加音频片段，长度：{len(chunk.audio_int16_bytes)} 字节")

        # total_audio_length = 0
        # for chunk in audio_chunks:
        #     if hasattr(chunk, "audio_int16_bytes") and chunk.audio_int16_bytes:
        #         chunk_length = len(chunk.audio_int16_bytes)
        #         total_audio_length += chunk_length
        #         self.player.add_audio(chunk.audio_int16_bytes)
        #         logger.info(f"添加音频片段，长度：{chunk_length} 字节")

        # # 3. 播放所有合成的音频
        # self.player.play_all()
        # logger.info(f"文字处理完成，累计合成音频长度：{total_audio_length} 字节")