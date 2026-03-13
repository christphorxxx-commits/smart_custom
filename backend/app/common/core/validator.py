import re
from typing import Annotated
from datetime import datetime
from backend.app.common.constant import RET
from backend.app.common.core.exceptions import CustomException
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema

# 自定义日期时间字符串类型
DateTimeStr = Annotated[
    datetime,
    AfterValidator(lambda x: datetime_validator(x)),
    PlainSerializer(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, datetime) else str(x), return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

# 自定义手机号类型
Telephone = Annotated[
    str,
    AfterValidator(lambda x: mobile_validator(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

# 自定义邮箱类型
Email = Annotated[
    str,
    AfterValidator(lambda x: email_validator(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]


def datetime_validator(value: str | datetime) -> datetime | None:
    """
    日期格式验证器。

    参数:
    - value (str | datetime): 日期值。

    返回:
    - datetime: 格式化后的日期。

    异常:
    - CustomException: 日期格式无效时抛出。
    """
    pattern = "%Y-%m-%d %H:%M:%S"
    try:
        if isinstance(value, str):
            return datetime.strptime(value, pattern)
        elif isinstance(value, datetime):
            return value
    except Exception:
        raise CustomException(code=RET.ERROR.code, msg="无效的日期格式")


def email_validator(value: str) -> str:
    """
    邮箱地址验证器。

    参数:
    - value (str): 邮箱地址。

    返回:
    - str: 验证后的邮箱地址。

    异常:
    - CustomException: 邮箱格式无效时抛出。
    """
    if not value:
        raise CustomException(code=RET.ERROR.code, msg="邮箱地址不能为空")

    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(regex, value):
        raise CustomException(code=RET.ERROR.code, msg="邮箱地址格式不正确")

    return value


def mobile_validator(value: str | None) -> str | None:
    """
    手机号验证器。

    参数:
    - value (str | None): 手机号。

    返回:
    - str | None: 验证后的手机号。

    异常:
    - CustomException: 手机号格式无效时抛出。
    """
    if not value:
        return value

    if len(value) != 11 or not value.isdigit():
        raise CustomException(code=RET.ERROR.code, msg="手机号格式不正确")

    regex = r'^1(3\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8[0-9]|9[0-9])\d{8}$'

    if not re.match(regex, value):
        raise CustomException(code=RET.ERROR.code, msg="手机号格式不正确")

    return value

def username_validator(value: str) -> str:
    v = value.strip()
    if not v:
        raise ValueError("账号不能为空")
    #字母开头，允许字母数字_.-
    if not re.match(r"^[A-Za-z][A-Za-z0-9_.-]{2,31}$", v):

        raise ValueError("账号需字母开头，3-32位，仅包含字母、数字和_.-")
    return v
