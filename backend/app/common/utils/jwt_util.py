import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from backend.app.common.core.config import settings


class JwtUtil:
    """JWT工具类"""

    @staticmethod
    def create_access_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌

        参数:
        - user_id (int): 用户ID
        - username (str): 用户名
        - expires_delta (Optional[timedelta]): 过期时间

        返回:
        - str: JWT令牌
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {
            "sub": str(user_id),
            "username": username,
            "exp": expire
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        解码令牌

        参数:
        - token (str): JWT令牌

        返回:
        - Dict[str, Any]: 解码后的载荷
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.PyJWTError:
            return {}
