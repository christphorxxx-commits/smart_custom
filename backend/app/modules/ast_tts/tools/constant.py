# -*- coding: utf-8 -*-
"""
配置管理模块
统一管理音频、WebSocket、模型等配置参数
"""

import pyaudio

# 音频配置
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 24000
CHUNK_SIZE = 1024

# WebSocket配置
WS_SERVER_URL = "ws://localhost:8765"
WS_HOST = "localhost"
WS_PORT = 8765

# 新增配置
MAX_TEXT_LENGTH = 2000  # 单请求最大文本长度，可根据实际需求调整

# 模型配置
MODEL_PATH = "backend/app/modules/ast_tts/tools/voice/zh_CN-huayan-medium.onnx"

# 服务端配置
MAX_CLIENTS = 10
CONNECTION_TIMEOUT = 30
SYNTHESIS_TIMEOUT = 300

# 客户端配置
MAX_CONCURRENT_TASKS = 5
AUDIO_QUEUE_SIZE = 50

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'