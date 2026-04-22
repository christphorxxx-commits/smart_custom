from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.common.core.base_model import ModelMixin, UserMixin
from backend.app.common.utils.common_util import uuid4_str


class UserModel(ModelMixin, UserMixin):
    """
    用户模型
    """
    __tablename__ = "sys_user"
    __table_args__ = {'comment': '用户表'}
    __loader_options__ = ["dept", "roles", "positions", "created_by", "updated_by"]  # 注意：是 created_by，不是 create_by

    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, comment="用户名/登录账号")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")  # ✅ 移除了 unique=True
    uuid: Mapped[str] = mapped_column(String(64), default=uuid4_str, nullable=False, unique=True,
                                      comment='UUID全局唯一标识')
    name: Mapped[str] = mapped_column(String(32), nullable=False, comment="昵称")
    mobile: Mapped[Optional[str]] = mapped_column(String(11), unique=True, comment="手机号")
    email: Mapped[Optional[str]] = mapped_column(String(64), unique=True, comment="邮箱")
    gender: Mapped[Optional[str]] = mapped_column(String(1), default='2', comment="性别(0:男,1:女,2:未知)")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否超管")
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="最后一次登录时间")  # ✅ 改为 nullable=True