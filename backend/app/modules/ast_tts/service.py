# import logging
# import os
# import queue
#
# import dashscope
# import websockets
#
# from backend.app.constant import WS_SERVER_URL
# from backend.app.modules.ast_tts.audio_player import AudioPlayer
#
# # 配置日志
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
#
# class AsrService:
#     # 初始化音频播放器
#     p = AudioPlayer()
#
#     audio_queue = queue.Queue()
#     """语音转文字，文字转语音服务层"""
#
#     @classmethod
#     async def asr_service(cls, file_path: str) -> str:
#         """
#         将路径中的录音转换为文字
#         :param file_path: 录音保存路径
#         :return: 转换后的文本
#         """
#         try:
#             if not os.path.exists(file_path):
#                 raise FileNotFoundError(f"音频文件不存在: {file_path}")
#
#             messages = [
#                 {"role": "system", "content": [{"text": ""}]},  # 配置定制化识别的 Context
#                 {"role": "user", "content": [{"audio": file_path}]}
#             ]
#
#             api_key = os.getenv("DASHSCOPE_API_KEY")
#             if not api_key:
#                 raise ValueError("DASHSCOPE_API_KEY 环境变量未配置")
#
#             response = dashscope.MultiModalConversation.call(
#                 api_key=api_key,
#                 model="qwen3-asr-flash",
#                 messages=messages,
#                 result_format="message",
#                 asr_options={
#                     "enable_itn": False
#                 }
#             )
#
#             text = response.output["choices"][0]["message"]["content"][0]["text"]
#             logger.info(f"ASR转换成功，识别结果: {text[:50]}...")
#             return text
#         except Exception as e:
#             logger.error(f"ASR转换失败: {e}", exc_info=True)
#             raise
#
#     @classmethod
#     async def getvoice_service(cls, text: str) -> str:
#         """
#         将文本转换成录音
#         :param text: 需要转换的文本
#         :return: 录音保存地址
#         """
#         try:
#             if not text:
#                 raise ValueError("转换文本不能为空")
#
#             api_key = os.getenv("DASHSCOPE_API_KEY")
#             if not api_key:
#                 raise ValueError("DASHSCOPE_API_KEY 环境变量未配置")
#
#             response = dashscope.MultiModalConversation.call(
#                 model="qwen3-tts-flash",
#                 api_key=api_key,
#                 text=text,
#                 voice="Cherry",
#                 language_type="Chinese",
#                 stream=False
#             )
#
#             audio_url = response.output["audio"]["url"]
#             logger.info(f"TTS转换成功，音频URL: {audio_url}")
#             return audio_url
#         except Exception as e:
#             logger.error(f"TTS转换失败: {e}", exc_info=True)
#             raise
#
#     @classmethod
#     async def tts_service(cls, text: str) -> bool:
#         """
#         连接推流服务端，接收音频并实时播放
#         :param text: 待转换的文本
#         :return: 转换是否成功
#         """
#         try:
#             if not text:
#                 raise ValueError("转换文本不能为空")
#
#             logger.info(f"开始TTS转换，文本长度: {len(text)}字")
#
#             async with websockets.connect(WS_SERVER_URL) as websocket:
#                 # 发送待转换的文字
#                 await websocket.send(text)
#                 logger.info(f"已发送文本到WebSocket服务器: {text[:50]}...")
#
#                 # 持续接收音频片段并播放
#                 async for audio_data in websocket:
#                     logger.debug(f"接收音频片段，长度: {len(audio_data)} 字节")
#                     # 实时播放（异步执行，避免阻塞接收）
#                     AsrService.p.add_audio(audio_data)
#
#             logger.info("TTS转换完成")
#             return True
#         except websockets.WebSocketException as e:
#             logger.error(f"WebSocket连接错误: {e}", exc_info=True)
#             raise
#         except Exception as e:
#             logger.error(f"TTS转换失败: {e}", exc_info=True)
#             raise
#
#
