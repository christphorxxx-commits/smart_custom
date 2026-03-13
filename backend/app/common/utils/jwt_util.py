import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from backend.app.common.core.exceptions import CustomException
from backend.app.config.setting import settings
from backend.app.modules.module_system.auth.schema import JWTPlayloadSchema

class JwtUtil:
    """JWT工具类"""

    @staticmethod
    def create_access_token(payload: JWTPlayloadSchema) -> str:
        """
        生成JWT访问令牌

        参数:
        - payload (JWTPayloadSchema): JWT有效载荷,包含用户信息等。

        返回:
        - str: 生成的JWT访问令牌。
        """
        payload_dict = payload.model_dump()


        return jwt.encode(
            payload_dict,
            settings.JWT_SECRET_KEY,
            algorithm=settings.ALGORITHM
        )


    @staticmethod
    def decode_token(token: str) -> JWTPlayloadSchema:
        """
        解析JWT访问令牌

        参数:
        - token (str): JWT访问令牌字符串。

        返回:
        - JWTPayloadSchema: 解析后的JWT有效载荷,包含用户信息等。

        异常:
        - CustomException: 解析失败时抛出,状态码为401。
        """
        if not token:
            raise CustomException(msg="认证不存在,请重新登录", code=10401, status_code=401)

        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.JWT_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            online_user_info = payload.get("sub")
            if not online_user_info:
                raise CustomException(msg="无效认证,请重新登录", code=10401, status_code=401)

            return JWTPlayloadSchema(**payload)

        except (jwt.InvalidSignatureError, jwt.DecodeError):
            raise CustomException(msg="无效认证,请重新登录", code=10401, status_code=401)

        except jwt.ExpiredSignatureError:
            raise CustomException(msg="认证已过期,请重新登录", code=10401, status_code=401)

        except jwt.InvalidTokenError:
            raise CustomException(msg="token已失效,请重新登录", code=10401, status_code=401)
