import whisper
import pyaudio
import wave
from backend.app.common.audio_player import AudioPlayer

audio = AudioPlayer()

# 1. 加载模型（可选不同大小，越小越轻量化，越大效果越好）
# tiny/base/small（CPU可跑） | medium/large（建议GPU）
model = whisper.load_model("small", device="cpu")  # device="cuda" 用GPU加速

# 方式1：识别本地音频文件（mp3/wav等）
def recognize_audio_file(audio_path):
    result = model.transcribe(audio_path, language="zh",audio=audio)  # 指定中文
    print("识别结果：", result["text"])
    return result["text"]

# 方式2：麦克风实时录音并识别（需PyAudio）
def recognize_microphone():
    # 录音参数
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Whisper推荐采样率
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "temp.wav"

    audio = pyaudio.PyAudio()
    # 开始录音
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("开始录音（5秒）...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("录音结束！")
    # 停止录音
    stream.stop_stream()
    stream.close()
    audio.terminate()
    # 保存临时文件
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    # 识别
    return recognize_audio_file(WAVE_OUTPUT_FILENAME)

# 测试
if __name__ == "__main__":
    # recognize_audio_file("test.wav")  # 识别文件
    recognize_microphone()  # 实时识别