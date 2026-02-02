from fastapi import APIRouter

from backend.app.modules.record.schema import RecordRequest, RecordResponse
from service import RecordService

RECORDRouter = APIRouter(prefix="/record",tags=["Record"])


@RECORDRouter.post("/audio")
async def record_audio(request: RecordRequest) -> RecordResponse:
    """
        麦克风录音接口
        - duration: 录音时长（秒）
        - sample_rate: 采样率
        - channels: 声道数（1=单声道，2=立体声）
        - save_path: 音频文件保存路径
        """
    await RecordService.record(request)