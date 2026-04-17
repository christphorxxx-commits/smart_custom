# ============ PostgreSQL SQLAlchemy AiApp 模型 ============
# -*- coding: utf-8 -*-

from typing import Optional, List, Dict, Any

from bson import ObjectId
from pydantic import Field
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.common.core.base_model import BaseMongoDocument, ModelMixin
from backend.app.common.utils.common_util import uuid4_str
from backend.app.modules.workflow.api.schema import LLMConfigSchema, KnowledgeBaseConfigSchema


class AiApp(ModelMixin):
    """AI应用 - PostgreSQL 表

    存储应用基本信息和权限控制，工作流配置详情存储在 MongoDB App 中

    架构说明：
        PG 表存储 app 基本信息和权限，用户可见性控制在这里
        MongoDB apps 集合存储完整的工作流节点边配置（nodes, edges）
        通过 uuid (uuid) 跨库关联
    """
    __tablename__ = "app"

    # 应用基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="应用名称")
    uuid: Mapped[str] = mapped_column(String(64), default=uuid4_str, nullable=False,
                                           unique=True, comment="应用唯一标识，对应MongoDB中的uuid")
    user_id: Mapped[int] = mapped_column(nullable=False, comment="创建用户ID（权限控制，引用sys_user.id）")
    description: Mapped[Optional[str]] = mapped_column(Text, default=None, nullable=True, comment="应用描述")
    icon: Mapped[Optional[str]] = mapped_column(String(20), default="🤖", comment="应用图标emoji")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否公开分享")
    type: Mapped[str] = mapped_column(String(20), default="workflow", comment="应用类型: workflow/ai/chat")

    model_config = {
        "arbitrary_types_allowed": True
    }


class App(BaseMongoDocument):
    """工作流应用模型

    用于保存前端创建的工作流应用信息，包含节点、边配置等
    所有系统配置字段都展开存储在顶层，和Schema结构完全对应
    """
    uuid: str = Field(default_factory=uuid4_str, description="应用UUID，用于跨库关联PG表")
    name: str = Field(..., description="应用名称")
    description: Optional[str] = Field(None, description="应用描述")
    user_id: Optional[str] = Field(default=None, description="创建用户ID")
    icon: Optional[str] = Field(default="🤖", description="应用图标emoji")
    type: str = Field(default="workflow", description="应用类型: WORKFLOW/CHAT")

    # 工作流结构定义
    nodes: List[Dict[str, Any]] = Field(default=[], description="节点列表，每个节点包含id, type, config")
    edges: List[Dict[str, Any]] = Field(default=[], description="边列表，每个边包含source, target, type")

    # 应用状态
    is_public: bool = Field(default=False, description="是否公开")
    version: int = Field(default=1, description="版本号")

    # ============ 通用系统配置 ============
    enableFileUpload: Optional[bool] = Field(default=False, description="是否启用文件上传")
    globalVariables: Optional[Dict[str, str]] = Field(default={}, description="全局变量字典")
    openingMessage: Optional[str] = Field(default=None, description="对话开场白")
    enableTTS: Optional[bool] = Field(default=False, description="是否启用语音播放")
    enableASR: Optional[bool] = Field(default=False, description="是否启用语音输入")
    guessedQuestions: Optional[bool] = Field(default=False, description="是否启用猜你想问")
    inputGuidance: Optional[bool] = Field(default=False, description="是否启用输入引导")

    # ============ 工作流Agent 特有配置 ============
    timeExecute: Optional[bool] = Field(default=False, description="是否定时执行")
    autoExecute: Optional[bool] = Field(default=False, description="是否自动执行")

    # ============ 对话式Agent 特有配置 ============
    llmConfig: Optional[LLMConfigSchema] = Field(default=None, description="大模型配置")
    enableKnowledgeBase: Optional[bool] = Field(default=False, description="是否启用知识库检索")
    knowledgeBaseConfig: Optional[KnowledgeBaseConfigSchema] = Field(default=None, description="知识库配置")
    enableToolCall: Optional[bool] = Field(default=False, description="是否启用工具调用")

    class Settings:
        name = "apps"  # MongoDB集合名称

    model_config = {
        "arbitrary_types_allowed": True
    }
