import os
import dashscope
import asyncio
import logging
import queue
import threading

import websockets

from tools.audio_player import AudioPlayer
from tools.constant import WS_SERVER_URL

p = AudioPlayer()

audio_queue = queue.Queue()


class AsrService:
    """语音转文字，文字转语音服务层"""

    @classmethod
    async def asr_service(cls,file_path:str) -> str:
        """
        将路径中的录音转换为文字
        :param file_path: 录音保存路径
        :return: 转换后的文本
        """
        audio_file_path = file_path

        messages = [
            {"role": "system", "content": [{"text": ""}]},  # 配置定制化识别的 Context
            {"role": "user", "content": [{"audio": audio_file_path}]}
        ]
        response = dashscope.MultiModalConversation.call(
            # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key = "sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen3-asr-flash",
            messages=messages,
            result_format="message",
            asr_options={
                # "language": "zh", # 可选，若已知音频的语种，可通过该参数指定待识别语种，以提升识别准确率
                "enable_itn": False
            }
        )
        print(response.output["choices"][0]["message"]["content"][0]["text"])
        return response.output["choices"][0]["message"]["content"][0]["text"]

    @classmethod
    async def getvoice_service(cls,text:str) -> str:
        """
        将文本转换成录音
        :param text: 需要转换的文本
        :return: 录音保存地址
        """
        response = dashscope.MultiModalConversation.call(
            model="qwen3-tts-flash",
            # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key = "sk-xxx"
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            text=text,
            voice="Cherry",
            language_type="Chinese",  # 建议与文本语种一致，以获得正确的发音和自然的语调。
            stream=False
        )
        print(response.output["audio"]["url"])
        return response.output["audio"]["url"]

    @classmethod
    async def tts_service(cls,text:str) :
        """连接推流服务端，接收音频并实时播放"""
        # 初始化音频播放器
        p = AudioPlayer()
        try:
            async with websockets.connect(WS_SERVER_URL) as websocket:
                # 发送待转换的文字
                await websocket.send(text)
                print(f"开始处理文字：{text[:50]}...（总长度：{len(text)}字）")

                # 持续接收音频片段并播放
                async for audio_data in websocket:
                    print(f"接收音频片段，长度：{len(audio_data)} 字节")

                    # 实时播放（异步执行，避免阻塞接收）
                    p.add_audio(audio_data)

            print("推流完成，客户端断开连接")
        except Exception as e:
            print(f"客户端出错：{e}")
            logging.error(f"客户端详细错误：{e}", exc_info=True)  # 打印完整的异常堆栈
        finally:
            p.close()


