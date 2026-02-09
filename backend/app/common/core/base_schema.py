from pydantic import BaseModel,ConfigDict,Field

from backend.app.common.core.validator import DateTimeStr


class UserInfoSchema(BaseModel):
    """用户信息模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, description="用户ID")
    name: str | None = Field(default=None, description="用户姓名")
    username: str | None = Field(default=None, description="用户名")


class BaseSchema(BaseModel):
    """通用输出模型，包含基础字段和审计字段"""
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, description="主键ID")
    uuid: str | None = Field(default=None, description="UUID")
    status: str = Field(default="0", description="状态")
    description: str | None = Field(default=None, description="描述")
    created_time: DateTimeStr | None = Field(default=None, description="创建时间")
    updated_time: DateTimeStr | None = Field(default=None, description="更新时间")

class CommonSchema(BaseModel):
    """通用信息模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="编号ID")
    name: str = Field(description="名称")


class UserBySchema(BaseModel):
    """通用创建模型，包含基础字段和审计字段"""
    model_config = ConfigDict(from_attributes=True)

    created_id: int | None = Field(default=None, description="创建人ID")
    created_by: UserInfoSchema | None = Field(default=None, description="创建人信息")
    updated_id: int | None = Field(default=None, description="更新人ID")
    updated_by: UserInfoSchema | None = Field(default=None, description="更新人信息")

