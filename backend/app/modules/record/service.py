from backend.app.modules.record.schema import RecordResponse, RecordRequest
from backend.app.common.core.logger import log
import os
import sounddevice as sd
import soundfile as sf

class RecordService:


    @classmethod
    async def record(cls, request : RecordRequest) -> RecordResponse:

        try:
            log.info(f"开始录音，时长{request.duration}秒，保存路径: {request.save_path}")

            # 1. 配置录音参数
            sd.default.samplerate = request.sample_rate
            sd.default.channels = request.channels

            # 2. 开始录音（阻塞式，直到录音时长结束）
            recording = sd.rec(
                int(request.duration * request.sample_rate),
                samplerate=request.sample_rate,
                channels=request.channels,
                dtype='int16'  # WAV格式常用的16位整型
            )
            sd.wait()  # 等待录音完成

            # 3. 保存录音为WAV文件
            sf.write(request.save_path, recording, request.sample_rate)

            # 检查文件是否保存成功
            if os.path.exists(request.save_path):
                file_size = os.path.getsize(request.save_path) / 1024  # 转成KB
                log.info(f"录音完成，文件大小: {file_size:.2f} KB")
                return RecordResponse(
                    success=True,
                    audio_path=os.path.abspath(request.save_path),
                    message=f"录音成功，文件已保存至: {os.path.abspath(request.save_path)}"
                )
            else:
                raise Exception("录音文件保存失败，文件不存在")

        except Exception as e:
            log.error(f"录音失败: {e}")
            # 清理可能生成的空文件
            if os.path.exists(request.save_path):
                os.remove(request.save_path)
            return RecordResponse(
                success=False,
                message=f"录音失败: {str(e)}"
            )

