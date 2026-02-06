from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class CurrentUserSchema(BaseModel):
    name: str | None = Field(default=None, max_length=32, description="名称")
    mobile: str | None = Field(default=None, description="手机号")
    email: EmailStr | None = Field(default=None, description="邮箱")
    gender: str | None = Field(default=None,description="性别")
