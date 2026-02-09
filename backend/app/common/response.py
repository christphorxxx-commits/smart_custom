from fastapi.responses import JSONResponse,StreamingResponse
from typing import Any
from pydantic import BaseModel,Field
from fastapi import status
from .constant import RET

class ResponseSchema(BaseModel):

    code: int = Field(default=RET.OK.code, description="业务状态码")
    msg: str = Field(default=RET.OK.msg, description="响应消息")
    data: Any = Field(default=None, description="响应数据")
    status_code:  int = Field(default=status.HTTP_200_OK, description="HTTP状态码")
    success: bool = Field(default=True, description="操作是否成功")


class SuccessResponse(JSONResponse):
    """成功响应类"""

    def __init__(
            self,
            data: Any = None,
            msg: str = RET.OK.msg,
            code: int = RET.OK.code,
            status_code: int = status.HTTP_200_OK,
            success: bool = True,
    ):
        """
        初始化成功响应类

        参数:
        - data (Any | None): 响应数据。
        - msg (str): 响应消息。
        - code (int): 业务状态码。
        - status_code (int): HTTP 状态码。
        - success (bool): 操作是否成功。

        返回:
        - None
        """
        content = ResponseSchema(
            code=code,
            msg=msg,
            data=data,
            status_code=status_code,
            success=success,
        ).model_dump()

        super().__init__(content=content,status_code=status_code)


class ErrorResponse(JSONResponse):
    """错误响应类"""

    def __init__(
            self,
            data: Any = None,
            msg: str = RET.ERROR.msg,
            code: int = RET.ERROR.code,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            success: bool = False
    ) -> None:
        """
        初始化错误响应类

        参数:
        - data (Any): 响应数据。
        - msg (str): 响应消息。
        - code (int): 业务状态码。
        - status_code (int): HTTP 状态码。
        - success (bool): 操作是否成功。

        返回:
        - None
        """
        content = ResponseSchema(
            code=code,
            msg=msg,
            data=data,
            status_code=status_code,
            success=success
        ).model_dump()
        super().__init__(content=content, status_code=status_code)
