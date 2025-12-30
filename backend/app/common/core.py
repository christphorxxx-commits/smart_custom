from piper import PiperVoice
from backend.app.constant import MODEL_PATH

voice = PiperVoice.load(MODEL_PATH)
print(f"成功加载Piper模型: {MODEL_PATH}")
