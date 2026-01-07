import os

import dashscope

from backend.app.common.core import logger



class ASRService:

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