import os
import wave
import struct
import asyncio

# 测试Demo2.wav文件的基本信息和内容
def test_audio_file():
    # Demo2.wav的完整路径
    audio_path = "d:\\pycharmWorkspace\\smart_custom\\backend\\app\\common\\Demo2.wav"
    
    try:
        print(f"开始测试音频文件: {audio_path}")
        
        # 检查文件是否存在
        if not os.path.exists(audio_path):
            print(f"错误: 音频文件不存在 - {audio_path}")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(audio_path)
        print(f"文件大小: {file_size} 字节")
        
        # 打开并分析WAV文件
        with wave.open(audio_path, 'rb') as wf:
            # 获取WAV文件信息
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            frames = wf.getnframes()
            duration = frames / float(frame_rate)
            
            print(f"音频格式: WAV")
            print(f"声道数: {channels}")
            print(f"采样宽度: {sample_width} 字节")
            print(f"采样率: {frame_rate} Hz")
            print(f"总帧数: {frames}")
            print(f"音频时长: {duration:.2f} 秒")
            
            # 读取少量音频数据验证内容
            chunk_size = 1024
            audio_data = wf.readframes(chunk_size)
            print(f"读取到的音频数据大小: {len(audio_data)} 字节")
            
            # 检查音频数据是否包含有效内容
            if audio_data:
                # 对于16位音频，检查是否有非零值
                if sample_width == 2:
                    # 16位音频，转换为整数
                    samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
                    max_sample = max(samples)
                    min_sample = min(samples)
                    print(f"音频样本范围: {min_sample} 到 {max_sample}")
                    
                    if max_sample > 100 or min_sample < -100:  # 简单判断是否有有效音频
                        print("✓ 音频数据包含有效内容")
                    else:
                        print("⚠ 音频数据可能为静音或音量极低")
                else:
                    print("✓ 音频数据存在")
            else:
                print("⚠ 未读取到音频数据")
        
        print("\n✅ 音频文件测试完成，文件格式正常！")
        return True
        
    except Exception as e:
        print(f"❌ 音频文件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_file():
    from backend.app.modules.asr.service import ASRService
    audio_path = "d:\\pycharmWorkspace\\smart_custom\\backend\\app\\common\\Demo2.wav"

    text = await ASRService.asr_whisper_service(audio_path)

    print(text)


# 运行测试
if __name__ == "__main__":
    asyncio.run(test_file())