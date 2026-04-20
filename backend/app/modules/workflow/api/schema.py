import operator
from typing import Literal, Dict, Any, TypedDict, Annotated, Optional, List

from pydantic import BaseModel, Field

from backend.app.common.enums import AgentType
from backend.app.common.utils.common_util import uuid4_str


class Node(BaseModel):
    """工作流节点基础模型"""
    id: str = Field(..., description="节点唯一ID")
    type: Literal["start", "llm", "router", "retrieve", "end"] = Field(..., description="节点类型")
    config: Dict[str, Any] = Field(default={}, description="节点配置字典")


class Edge(BaseModel):
    """工作流边模型"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    type: Literal["normal", "conditional"] = Field(..., description="边类型")
    condition: str | None = Field(default=None, description="条件表达式（router节点专用）")


class State(TypedDict, total=False):
    input: str  # 用户输入（只读）
    messages: Annotated[list, operator.add]  # 对话上下文（累加）
    variables: dict  # 节点输出（按节点存储）
    decision: str  # 路由决策（临时）
    output: str  # 最终输出


# ============ LLM 配置 ============
class LLMConfigSchema(BaseModel):
    """LLM配置schema"""
    model: Optional[str] = Field(None, description="模型名称")
    systemPrompt: Optional[str] = Field(None, description="系统提示词")
    temperature: Optional[float] = Field(None, description="温度")
    maxTokens: Optional[int] = Field(None, description="最大token数")


# ============ 知识库配置 ============
class KnowledgeBaseConfigSchema(BaseModel):
    """知识库配置schema"""
    collectionId: Optional[str] = Field(None, description="知识库集合ID")
    topK: Optional[int] = Field(5, description="返回结果数量")
    scoreThreshold: Optional[float] = Field(0.5, description="相似度阈值")


# ============ 对话式Agent 完整配置schema ============
class SystemConfigSchema(BaseModel):
    """Agent完整系统配置schema"""
    enableFileUpload: Optional[bool] = Field(default=False, description="是否启用文件上传")
    globalVariables: Optional[Dict[str, str]] = Field(default={}, description="全局变量字典")
    openingMessage: Optional[str] = Field(default=None, description="对话开场白")
    enableTTS: Optional[bool] = Field(default=False, description="是否启用语音播放")
    enableASR: Optional[bool] = Field(default=False, description="是否启用语音输入")
    guessedQuestions: Optional[bool] = Field(default=False, description="是否启用猜你想问")
    inputGuidance: Optional[bool] = Field(default=False, description="是否启用输入引导")


class WorkflowSystemConfigSchema(SystemConfigSchema):
    """工作流Agent系统配置"""
    timeExecute: bool = Field(default=False, description="是否定时执行")
    autoExecute: Optional[bool] = Field(default=False, description="是否自动执行")


class ChatSystemConfigSchema(SystemConfigSchema):
    """对话式Agent系统配置"""
    llmConfig: LLMConfigSchema = Field(
        default=LLMConfigSchema(
            model="qwen-max",
            systemPrompt="你是一个智能AI助手",
            temperature=0.7, maxTokens=5000
        ),
        description="大模型配置"
    )
    enableKnowledgeBase: Optional[bool] = Field(default=False, description="是否启用知识库检索")
    knowledgeBaseConfig: Optional[KnowledgeBaseConfigSchema] = Field(default=None, description="知识库配置")
    enableToolCall: Optional[bool] = Field(default=False, description="是否启用工具调用")


# ============ 基础共享 schema ============
class CreateAppPGSchema(BaseModel):
    """PostgreSQL 创建应用 schema - 只保留 PG 需要的基本字段"""
    name: str = Field(..., description="Agent名称（必填）")
    uuid: Optional[str] = Field(default_factory=uuid4_str, description="应用UUID（后端生成）")
    user_id: Optional[int] = Field(None, description="创建用户ID（后端填充）- PG 外键引用 sys_user.id，必须 int")
    description: Optional[str] = Field(default=None, description="Agent描述（可选）")
    icon: Optional[str] = Field("🤖", description="图标emoji，默认 🤖")
    type: Optional[AgentType] = Field(AgentType.WORKFLOW, description="Agent类型: WORKFLOW/CHAT（前端自动设置）")
    is_public: bool = Field(default=False, description="是否公开分享，默认不公开")


class CreateAppSchema(CreateAppPGSchema, SystemConfigSchema):
    """应用完整创建 schema（包含所有字段，用于创建后同时写入 PG + MongoDB）

    创建规则：
    - 只有 name 是必填项
    - description/icon/is_public/type 都有默认值，可省略
    - type 由前端点击创建按钮自动设置 (WORKFLOW/CHAT)
    - SystemConfigSchema 所有配置字段都使用默认值，创建后在编辑阶段设置
    """
    nodes: Optional[List[Dict[str, Any]]] = Field(default=[], description="初始节点列表（工作流Agent）")
    edges: Optional[List[Dict[str, Any]]] = Field(default=[], description="初始边列表（工作流Agent）")
    version: Optional[int] = Field(default=1, description="版本号")


# ============ 工作流Agent（可视化编排） ============
class UpdateWorkflowAgentSchema(CreateAppSchema, WorkflowSystemConfigSchema):
    """更新工作流Agent请求（可视化编排）"""
    app_id: int = Field(..., description="app的唯一id")


# ============ 对话式Agent（配置式，默认线性） ============
class UpdateChatAgentSchema(CreateAppSchema, ChatSystemConfigSchema):
    """更新对话式Agent请求

    对话式Agent自动生成线性工作流：
    - 默认: start → llm → end
    - 启用知识库后: start → retrieve → llm → end
    """
    app_id: int = Field(..., description="app的唯一id")


class AppInfoSchema(BaseModel):
    app_id: int = Field(..., description="app的唯一id")
    uuid: Optional[str] = Field(None, description="应用UUID（后端生成）")
    name: str = Field(..., description="Agent名称（必填）")
    description: Optional[str] = Field(None, description="Agent描述（可选）")
    icon: Optional[str] = Field("🤖", description="图标emoji，默认 🤖")
    type: Optional[str] = Field(None, description="Agent类型: WORKFLOW/CHAT（前端自动设置）")
    is_public: bool = Field(default=False, description="是否公开分享，默认不公开")


class AppDetailResponseSchema(CreateAppSchema):
    """获取应用详情响应 schema
    - id: MongoDB 文档 ObjectId 转换为字符串
    - pg_id: PostgreSQL 主键 ID
    - uuid: 应用 UUID，跨库关联使用
    """
    # 工作流特有配置
    timeExecute: Optional[bool] = Field(default=False, description="是否定时执行")
    autoExecute: Optional[bool] = Field(default=False, description="是否自动执行")
    # 对话式 Agent 特有配置
    llmConfig: Optional[LLMConfigSchema] = Field(default=None, description="大模型配置")
    enableKnowledgeBase: Optional[bool] = Field(default=False, description="是否启用知识库检索")
    knowledgeBaseConfig: Optional[KnowledgeBaseConfigSchema] = Field(default=None, description="知识库配置")
    enableToolCall: Optional[bool] = Field(default=False, description="是否启用工具调用")

    model_config = {
        "arbitrary_types_allowed": True
    }
