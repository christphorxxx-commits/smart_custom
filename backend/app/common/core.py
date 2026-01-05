import logging

from fastapi import WebSocket
from piper.voice import PiperVoice

from backend.app.common.constant import MODEL_PATH

#Piper模型初始化
voice = PiperVoice.load(MODEL_PATH)
print(f"成功加载Piper模型: {MODEL_PATH}")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------
# 核心：WebSocket 连接管理器
# --------------------------
class ConnectionManager:
    def __init__(self):
        # 存储不同路径的 WebSocket 连接：key=路径，value=连接列表
        self.active_connections: dict[str, list[WebSocket]] = {}

    # 新增连接（按路径分类）
    async def connect(self, websocket: WebSocket, path: str):
        await websocket.accept()
        if path not in self.active_connections:
            self.active_connections[path] = []
        self.active_connections[path].append(websocket)
        logging.info(f"WebSocket 连接成功：{path}，当前连接数：{len(self.active_connections[path])}")

    # 移除连接
    def disconnect(self, websocket: WebSocket, path: str):
        if path in self.active_connections:
            self.active_connections[path].remove(websocket)
            logging.info(f"WebSocket 断开连接：{path}，剩余连接数：{len(self.active_connections[path])}")

    # 向指定路径的所有连接发送消息
    async def send_to_path(self, message: str, target_path: str):
        if target_path in self.active_connections:
            for connection in self.active_connections[target_path]:
                await connection.send_text(message)

    # 跨路径转发消息（比如从 /ws 转发到 /ws2，反之亦然）
    async def forward_message(self, message: str, from_path: str, to_path: str):
        # 1. 向目标路径发送消息
        await self.send_to_path(f"来自 {from_path} 的消息：{message}", to_path)
        # 2. 给发送方返回确认（可选）
        await self.send_to_path(f"已转发消息到 {to_path}：{message}", from_path)

# 初始化全局管理器（所有 WebSocket 共用）
manager = ConnectionManager()


#llm
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3:0.6b"
)
