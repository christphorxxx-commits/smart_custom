from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field, BaseModel, EmailStr, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.modules.module_system.user.model import UserModel


class AuthSchema(BaseModel):
    """权限认证模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: UserModel | None = Field(default=None,description="用户信息")
    check_data_scope: bool = Field(default=True, description="是否检查数据权限")
    db: AsyncSession = Field(description="数据库会话")

class LoginSchema(BaseModel):
    """登录请求模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    mobile: Optional[str] = Field(default=None, description="手机号")
    email: Optional[EmailStr] = Field(default=None, description="邮箱")
    password: str = Field(...,max_length=128,description="密码")

class JWTPlayloadSchema(BaseModel):
    """JWT载荷模型"""
    sub: str = Field(..., description='用户登录信息，暂时使用user_id')
    is_refresh: bool = Field(default=False, description="是否刷新token")
    exp: datetime | int = Field(...,description='过期时间')

    @model_validator(mode='after')
    def validate(self):
        if not self.sub or len(self.sub) == 0:
            raise ValueError("用户id不能为空")
        return self


class JWTOutSchema(BaseModel):
    """JWT响应模型"""
    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., min_length=1, description='访问token')
    refresh_token: str = Field(..., min_length=1, description='刷新token')
    token_type: str = Field(default='Bearer', description='token类型')
    expires_in: int = Field(..., gt=0, description='过期时间(秒)')


class RefreshTokenSchema(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., min_length=1, description='刷新token')