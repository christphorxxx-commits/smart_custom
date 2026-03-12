from pwdlib import PasswordHash

from backend.app.common.utils.hash_bcrpy_util import PwdUtil

password = "123456"

pwd_hash = PwdUtil.set_password_hash(password)

print(pwd_hash)

print(PwdUtil.verify(password, pwd_hash))