from pydantic import BaseModel
from typing import Optional

class RecordRequest(BaseModel):
    duration: int
    sample_rate: int = 16000
    channels: int = 1
    save_path : str = "./recorded.wav"

class RecordResponse(BaseModel):
    success: bool
    audio_path: Optional[str] = None
    message: str

