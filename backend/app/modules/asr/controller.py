from fastapi import APIRouter,HTTPException

from backend.app.common.core.core import logger
from backend.app.modules.asr.schema import ASRResponse, ASRRequest
from backend.app.modules.asr.service import ASRService

ASRRouter = APIRouter(prefix="/asr", tags=["ASR"])


@ASRRouter.post("/asr", response_model=ASRResponse)
async def speech_to_text(request: ASRRequest):
    try:
        audio_data = request.audio_path or request.audio_file
        if not audio_data:
            raise  HTTPException(status_code=400, detail="需要提供音频文件路径或URL")

        logger.info(f"收到ASR请求: {audio_data}")

        #调用asr服务，获得语音转成后的文字
        speech_text = await ASRService.asr_service(audio_data)

        return ASRResponse(
            success=True,
            text=speech_text,
            message="ASR转换成功"
        )

    except Exception as e:
        logger.error(f"ASR转换失败: {e}")
        return ASRResponse(
            success=False,
            message=f"ASR转换失败: {str(e)}"
        )


