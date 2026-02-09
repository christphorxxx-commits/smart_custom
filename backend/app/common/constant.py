# 新增配置
from enum import Enum

MAX_TEXT_LENGTH = 2000  # 单请求最大文本长度，可根据实际需求调整

# 音频配置
AUDIO_FORMAT = 8  # pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 24000
CHUNK_SIZE = 1024

# 模型配置
MODEL_PATH = "D:/pycharmWorkspace/smart_custom/backend/app/common/voice/zh_CN-huayan-medium.onnx"

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

class RET(Enum):
    """
    系统返回码举例

    2~200: 成功状态码
    400~600： HTTP标准错误码
    4000+：自定义业务错误码
    """

    # 成功状态码
    OK = (0, "成功")
    SUCCESS = (200, "操作成功")
    CREATED = (201, "创建成功")
    ACCEPTED = (202, "请求已接受")
    NO_CONTENT = (204, "操作成功,无返回数据")

    # HTTP标准错误码
    ERROR = (1, "请求错误")
    BAD_REQUEST = (400, "参数错误")
    UNAUTHORIZED = (401, "未授权")
    FORBIDDEN = (403, "访问受限")
    NOT_FOUND = (404, "资源不存在")
    BAD_METHOD = (405, "不支持的请求方法")
    NOT_ACCEPTABLE = (406, "不接受的请求")
    CONFLICT = (409, "资源冲突")
    GONE = (410, "资源已删除")
    PRECONDITION_FAILED = (412, "前提条件失败")
    UNSUPPORTED_MEDIA_TYPE = (415, "不支持的媒体类型")
    UNPROCESSABLE_ENTITY = (422, "无法处理的实体")
    TOO_MANY_REQUESTS = (429, "请求过于频繁")

    # 自定义业务错误码
    EXCEPTION = (-1, "系统异常")
    DATAEXIST = (4003, "数据已存在")
    DATAERR = (4004, "数据错误")
    PARAMERR = (4103, "参数错误")
    IOERR = (4302, "IO错误")
    SERVERERR = (4500, "服务错误")
    UNKOWNERR = (4501, "未知错误")
    TIMEOUT = (4502, "请求超时")
    RATE_LIMIT_EXCEEDED = (4503, "访问频率超限")

    # Token相关错误码
    INVALID_TOKEN = (4504, "无效令牌")
    EXPIRED_TOKEN = (4505, "令牌过期")

    def __init__(self, code: int, msg: str):
        """
        初始化返回码。

        参数:
        - code (int): 错误码。
        - msg (str): 错误信息。

        返回:
        - None
        """
        self._code = code
        self._msg = msg

    @property
    def code(self) -> int:
        """获取错误码"""
        return self._code

    @property
    def msg(self) -> str:
        """获取错误信息"""
        return self._msg