# import asyncio
# import websockets
# from piper.voice import PiperVoice  # 确保piper库正确安装
#
# from tools.constant import MODEL_PATH, WS_HOST, WS_PORT
#
# # 预加载Piper模型（避免每次连接都重新加载，提升性能）
# try:
#     voice = PiperVoice.load(MODEL_PATH)
#     print(f"成功加载Piper模型: {MODEL_PATH}")
# except Exception as e:
#     print(f"加载Piper模型失败: {e}")
#     voice = None
#
#
# async def tts_stream_handler(websocket):
#     """处理单个客户端的推流请求：接收文字，推送音频片段"""
#     print(f"客户端已连接：{websocket.remote_address}")
#     try:
#         # 接收客户端发送的文字（单次接收，也可改为持续接收）
#         text = await websocket.recv()
#         if not text:
#             await websocket.close(reason="空文字内容")
#             return
#
#         print(f"开始处理文字：{text[:20]}...（总长度：{len(text)}字）")
#
#         # 核心：边生成音频片段，边推送给客户端
#         for chunk in voice.synthesize(text):
#             if chunk.audio_int16_bytes:
#                 audio_data = chunk.audio_int16_bytes
#                 # 推流：发送音频字节数据给客户端
#                 await websocket.send(audio_data)
#                 print(f"推送音频片段，长度：{len(audio_data)} 字节")
#
#         print(f"文字处理完成，已推送所有音频片段")
#     except websockets.exceptions.ConnectionClosedError as e:
#         print(f"客户端断开连接：{e}")
#     except Exception as e:
#         print(f"处理请求出错：{e}")
#         await websocket.close(reason=f"服务端错误：{str(e)}")
#
# async def start_tts_stream_server():
#     """启动WebSocket推流服务"""
#     async with websockets.serve(tts_stream_handler, WS_HOST, WS_PORT):
#         print(f"Piper TTS推流服务已启动：ws://{WS_HOST}:{WS_PORT}")
#         await asyncio.Future()  # 保持服务运行
#
# if __name__ == "__main__":
#     # 运行服务端
#     asyncio.run(start_tts_stream_server())