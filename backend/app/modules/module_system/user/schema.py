from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

from backend.app.common.core.base_schema import BaseSchema, UserBySchema, CommonSchema
from backend.app.common.core.validator import mobile_validator, username_validator, DateTimeStr


class CurrentUserUpdateSchema(BaseModel):
    """基础用户信息"""
    name: str | None = Field(default=None, max_length=32, description="名称")
    mobile: str | None = Field(default=None, description="手机号")
    email: EmailStr | None = Field(default=None, description="邮箱")
    gender: str | None = Field(default=None, description="性别")
    avatar: str | None = Field(default=None, description="头像")

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value: str | None):
        return mobile_validator(value)

    # @field_validator("avatar")
    # @classmethod
    # def validate_avatar(cls, value: str | None):
    #     if not value:
    #         return value
    #     parsed = urlparse(value)
    #     if parsed.scheme in ("http", "https") and parsed.netloc:
    #         return value
    #     raise ValueError("头像地址需为有效的HTTP/HTTPS URL")

class CurrentUserSchema(BaseModel):
    name: Optional[str] = Field(default=None, max_length=32, description="名称")
    mobile: Optional[str] = Field(default=None, description="手机号")
    email: Optional[EmailStr] = Field(default=None, description="邮箱")
    gender: Optional[str] = Field(default=None,description="性别")


class UserRegisterSchema(BaseModel):
    name: Optional[str] = Field(default=None,max_length=32,description="名称")
    mobile: Optional[str] = Field(default=None,description="手机号")
    username: str = Field(...,max_length=32,description="账号")
    password: str = Field(...,max_length=128,description="密码")
    created_id: Optional[int] = Field(default=1,description="创建人id")
    description: Optional[str] = Field(default=None, max_length= 255,description="备注")

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value: Optional[str] = None):
        return mobile_validator(value)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: Optional[str] = None):
        return username_validator(value)

class UserCreateSchema(CurrentUserUpdateSchema):
    """新增"""
    model_config =ConfigDict(from_attributes=True)

    username: Optional[str] = Field(default=None, max_length=32, description="用户名")
    password: Optional[str] = Field(default=None, max_length=128, description="密码哈希值")

class UserUpdateSchema(UserCreateSchema):
    """更新"""
    model_config = ConfigDict(from_attributes=True)

    last_login: DateTimeStr | None = Field(default=None, description="最后登录时间")

class UserOutSchema(UserUpdateSchema, BaseSchema, UserBySchema):
    """响应"""
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
    gitee_login: Optional[str] = Field(default=None, max_length=32, description="Gitee登录")
    github_login: Optional[str] = Field(default=None, max_length=32, description="Github登录")
    wx_login: Optional[str] = Field(default=None, max_length=32, description="微信登录")
    qq_login: Optional[str] = Field(default=None, max_length=32, description="QQ登录")
    # dept_name: str | None = Field(default=None, description='部门名称')
    # dept: CommonSchema | None = Field(default=None, description='部门')
    # positions: list[CommonSchema] | None = Field(default=[], description='岗位')
    # roles: list[RoleOutSchema] | None = Field(default=[], description='角色')
    # menus: list[MenuOutSchema] | None = Field(default=[], description='菜单')