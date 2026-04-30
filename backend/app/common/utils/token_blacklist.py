"""
Token黑名单管理 - 用于登出时使token失效
使用内存存储（生产环境建议使用Redis）
"""
import time
from typing import Set, Dict
from collections import defaultdict

from backend.app.common.utils.jwt_util import JwtUtil


class TokenBlacklist:
    """Token黑名单"""

    def __init__(self):
        # 存储格式: {user_uuid: {token1, token2, ...}}
        self._blacklist: Dict[str, Set[str]] = defaultdict(set)
        # 清理过期token的时间间隔（秒）
        self._cleanup_interval = 3600  # 1小时
        self._last_cleanup = time.time()

    def add(self, token: str) -> None:
        """
        将token加入黑名单

        Args:
            token: JWT token字符串
        """
        try:
            payload = JwtUtil.decode_token(token)
            user_uuid = payload.sub
            self._blacklist[user_uuid].add(token)

            # 定期清理过期token
            self._cleanup_if_needed()
        except Exception:
            # token无效时直接忽略
            pass

    def is_blacklisted(self, token: str) -> bool:
        """
        检查token是否在黑名单中

        Args:
            token: JWT token字符串

        Returns:
            bool: True=在黑名单中, False=不在
        """
        try:
            payload = JwtUtil.decode_token(token)
            user_uuid = payload.sub
            return token in self._blacklist.get(user_uuid, set())
        except Exception:
            # token无效时认为已"失效"
            return True

    def remove_user_tokens(self, user_uuid: str) -> None:
        """
        清除指定用户的所有token（强制登出所有会话）

        Args:
            user_uuid: 用户UUID
        """
        if user_uuid in self._blacklist:
            del self._blacklist[user_uuid]

    def _cleanup_if_needed(self) -> None:
        """清理已过期的token"""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now
        to_remove = []

        for user_uuid, tokens in self._blacklist.items():
            valid_tokens = set()
            for token in tokens:
                try:
                    # 验证token是否未过期
                    JwtUtil.decode_token(token)
                    valid_tokens.add(token)
                except Exception:
                    # token已过期，无需保留
                    continue

            if valid_tokens:
                self._blacklist[user_uuid] = valid_tokens
            else:
                to_remove.append(user_uuid)

        # 清理空的用户条目
        for user_uuid in to_remove:
            del self._blacklist[user_uuid]


# 全局单例
token_blacklist = TokenBlacklist()
