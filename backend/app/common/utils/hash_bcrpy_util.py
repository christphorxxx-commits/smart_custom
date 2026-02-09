from passlib.context import CryptContext


PwdContext = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class PwdUtil:
    """
    密码工具类
    """
    @classmethod
    def verify(cls, plain_password : str, hashed_password : str) -> bool:
        """
        校验密码是否匹配

        :param plain_password:原文密码
        :param hashed_password:哈希后的密码
        :return:
        """

        return PwdContext.verify(plain_password, hashed_password)

    @classmethod
    def set_password_hash(cls,password :str) -> str:
        """
                对密码进行加密

                参数:
                - password (str): 明文密码。

                返回:
                - str: 加密后的密码哈希值。
                """
        return PwdContext.hash(password)

    @classmethod
    def check_password(cls,password : str) -> str | None:
        """
                检查密码强度

                参数:
                - password (str): 明文密码。

                返回:
                - str | None: 如果密码强度不够返回提示信息,否则返回None。
                """
        if len(password) < 6:
            return "密码长度至少6位"
        if not any(c.isupper() for c in password):
            return "密码需要包含大写字母"
        if not any(c.islower() for c in password):
            return "密码需要包含小写字母"
        if not any(c.isdigit() for c in password):
            return "密码需要包含数字"
        return None