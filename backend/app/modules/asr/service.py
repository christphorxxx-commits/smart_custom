import asyncio
import os

import whisper
from dotenv import load_dotenv
load_dotenv()
import dashscope

from backend.app.common.core.core import logger



class ASRService:
    # 类变量存储模型实例，避免重复加载
    _whisper_model = None
    _model_config = {
        "model_name": "small",
        "device": "cpu"
    }



    def _init_whisper_model(self):
        """初始化Whisper模型（仅在首次使用时加载）"""
        if self._whisper_model is None:
            logger.info(f"加载Whisper模型: {self._model_config['model_name']}，设备: {self._model_config['device']}")
            self._whisper_model = whisper.load_model(
                self._model_config['model_name'],
                device=self._model_config['device']
            )

    @classmethod
    async def asr_whisper_service(cls, file_path: str) -> str:
        """
        使用本地Whisper模型将音频文件转换为文字
        :param file_path: 音频文件路径
        :return: 转换后的文本
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"音频文件不存在: {file_path}")

            # 初始化模型（仅首次加载）
            cls._init_whisper_model()

            # 使用线程池执行同步的transcribe操作，避免阻塞事件循环
            loop = asyncio.get_event_loop()

            # 使用lambda函数包装transcribe调用，正确传递关键字参数
            result = await loop.run_in_executor(
                None,
                lambda: cls._whisper_model.transcribe(audio=file_path, language="zh")
            )

            logger.info(f"Whisper识别成功，结果: {result['text'][:50]}...")
            return result['text']
        except FileNotFoundError as e:
            logger.error(f"Whisper识别失败: {e}")
            raise
        except Exception as e:
            logger.error(f"Whisper识别发生意外错误: {e}", exc_info=True)
            raise

    @classmethod
    async def asr_service(cls, file_path: str) -> str:
        """
        将路径中的录音转换为文字
        :param file_path: 录音保存路径
        :return: 转换后的文本
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"音频文件不存在: {file_path}")

            messages = [
                {"role": "system", "content": [{"text": ""}]},  # 配置定制化识别的 Context
                {"role": "user", "content": [{"audio": file_path}]}
            ]

            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("DASHSCOPE_API_KEY 环境变量未配置")

            response = dashscope.MultiModalConversation.call(
                api_key=api_key,
                model="qwen3-asr-flash",
                messages=messages,
                result_format="message",
                asr_options={
                    "enable_itn": False
                }
            )

            text = response.output["choices"][0]["message"]["content"][0]["text"]
            logger.info(f"ASR转换成功，识别结果: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"ASR转换失败: {e}", exc_info=True)
            raise