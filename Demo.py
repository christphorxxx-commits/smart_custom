from __future__ import annotations
from datetime import timedelta, timedelta, timezone, datetime
from typing import Annotated

import uvicorn

import jwt
from fastapi import Depends, FastAPI, HTTPException,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "e8ebdf3c97ae4e8b1235d5d084f80461695369f99b12dc4ce11ec22f76b27a63"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

app = FastAPI()

#哈希算法保存明文密码再存入数据库
def fake_hash_password(password: str):
    return "fakehashed" + password


#用户字段模型
class User(BaseModel):
    username: str
    email: str | None =None
    full_name: str | None = None
    disabled: bool | None = None

#哈西密码模型
class UserInDB(User):
    hashed_password: str

password_hash = PasswordHash.recommended()


#它的作用是从请求头 Authorization: Bearer <token> 中提取 <token> 字符串。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)


#从数据库中读取用户信息，返回用户在数据库中的哈希密码
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None =  None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#虚拟解码token
def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

#得到当前登录用户信息，返回当前用户
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)

    if user is None:
        raise credentials_exception
    return user

    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
            )
    return user

#获取当前活跃用户信息，disabled=False为当前活跃
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm,Depends()]
) -> Token:
    user = authenticate_user(fake_users_db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        #sub是前缀，这里标识前缀为username：johndoe
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token,token_type="bearer")


#注册，user_dict为当前注册用户信息字段，根据传入表格中的username字段到数据库中匹配
# @app.post("/token")
# async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#
#     #得到user
#     user = UserInDB(**user_dict)
#     #计算纯表单传入的password的哈希值
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#
#     return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

# @app.post("/items/")
# async def get_items(token: Annotated[str, Depends(oauth2_scheme)]):
#
#     return {"token":token}
    # """
    #     curl -X 'POST' \
    #     'http://127.0.0.1:18081/items/' \
    #     -H 'accept: application/json' \
    #     -H 'Content-Type: application/x-www-form-urlencoded' \
    #     -d 'grant_type=password&username=user_test&password=user_password&scope=test_scope&client_id=test_client_id&client_secret=test_client_secret'
    #
    #     {
    #         "grant_type": "password",
    #         "username": "user_test",
    #         "password": "user_password",
    #         "scopes": [
    #           "test_scope"
    #         ],
    #         "client_id": "test_client_id",
    #         "client_secret": "test_client_secret"
    #     }
    # """
    # print(
    #     'username:',oauth2_data.username,
    #     '\npassword:',oauth2_data.password,
    #     '\nscopes:',oauth2_data.scopes,
    #     '\nclient_id:',oauth2_data.client_id,
    #     '\nclient_secret:',oauth2_data.client_secret,
    #     '\ngrant_type:password',
    # )
    #
    # return dict(oauth2_data.__dict__.items())

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)