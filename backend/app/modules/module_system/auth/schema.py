from pydantic import ConfigDict, Field,BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.modules.module_system.user.model import UserModel


class AuthSchema(BaseModel):
    """权限认证模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: UserModel | None = Field(default=None,description="用户信息")
    check_data_scope: bool = Field(default=True, description="是否检查数据权限")
    db: AsyncSession = Field(description="数据库会话      ")