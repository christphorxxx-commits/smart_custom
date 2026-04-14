import operator
from typing import Literal, Dict, Any, TypedDict, Annotated, Optional, List

from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    type: Literal["start", "llm", "router", "end"]
    config: Dict[str, Any] = {}


class Edge(BaseModel):
    source: str
    target: str
    type: Literal["normal", "conditional"]
    condition: str | None = None  # router用


class State(TypedDict, total=False):
    input: str  # 用户输入（只读）
    messages: Annotated[list, operator.add]  # 对话上下文（累加）
    variables: dict  # 节点输出（按节点存储）
    decision: str  # 路由决策（临时）
    output: str  # 最终输出
# ============ Pydantic 请求模型 ============
class CreateWorkflowSchema(BaseModel):
    """创建工作流请求"""
    name: str = Field(..., description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    icon: Optional[str] = Field(None, description="图标emoji")
    nodes: List[Dict[str, dict]] = Field(..., description="节点列表")
    edges: List[Dict[str, dict]] = Field(..., description="边列表")
    is_public: bool = Field(default=False, description="是否公开")


class UpdateWorkflowSchema(BaseModel):
    """更新工作流请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    nodes: Optional[List[Dict[str, dict]]] = None
    edges: Optional[List[Dict[str, dict]]] = None
    is_public: Optional[bool] = None

class AppInfoSchema(BaseModel):
    """应用信息返回字段"""
    id: int
    app_id: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    type: str
    is_public: bool


class AppResponseSchema(BaseModel):
    """应用详情返回schema - 完整工作流配置"""
    id: str = Field(..., description="MongoDB ObjectId 字符串")
    app_id: str = Field(..., description="应用UUID，用于跨库关联PG表")
    name: str = Field(..., description="应用名称")
    description: Optional[str] = Field(None, description="应用描述")
    user_id: Optional[str] = Field(None, description="创建用户ID")
    icon: Optional[str] = Field(None, description="图标emoji")
    type: str = Field(..., description="应用类型: workflow/ai/chat")
    nodes: List[Dict[str, Any]] = Field(..., description="节点列表，每个节点包含id, type, config")
    edges: List[Dict[str, Any]] = Field(..., description="边列表，每个边包含source, target, type")
    is_public: bool = Field(default=False, description="是否公开分享")
    version: int = Field(default=1, description="版本号")
