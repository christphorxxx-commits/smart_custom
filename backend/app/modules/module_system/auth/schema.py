from pydantic import ConfigDict, Field,BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.modules.module_system.user.model import UserModel


class AuthSchema(BaseModel):
    """权限认证模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: UserModel | None = Field(default=None,description="用户信息")
    check_data_scope: bool = Field(default=True, description="是否检查数据权限")
    db: AsyncSession = Field(description="数据库会话")

class JWTOutSchema(BaseModel):
    """JWT响应模型"""
    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., min_length=1, description='访问token')
    refresh_token: str = Field(..., min_length=1, description='刷新token')
    token_type: str = Field(default='Bearer', description='token类型')
    expires_in: int = Field(..., gt=0, description='过期时间(秒)')