import operator
from typing import Literal, Dict, Any, TypedDict, Annotated, Optional, List

from pydantic import BaseModel, Field


class Node(BaseModel):
    """工作流节点基础模型"""
    id: str = Field(..., description="节点唯一ID")
    type: Literal["start", "llm", "router", "end"] = Field(..., description="节点类型")
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
# ============ Pydantic 请求模型 ============
class CreateAppSchema(BaseModel):
    """创建工作流请求"""
    name: str = Field(..., description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    icon: Optional[str] = Field(None, description="图标emoji")
    nodes: List[Dict[str, Any]] = Field(..., description="节点列表")
    edges: List[Dict[str, Any]] = Field(..., description="边列表")
    is_public: bool = Field(default=False, description="是否公开")


class UpdateAppSchema(BaseModel):
    """更新工作流请求"""
    name: Optional[str] = Field(None, description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    icon: Optional[str] = Field(None, description="图标emoji")
    nodes: Optional[List[Dict[str, Any]]] = Field(None, description="节点列表")
    edges: Optional[List[Dict[str, Any]]] = Field(None, description="边列表")
    is_public: Optional[bool] = Field(None, description="是否公开")

class AppInfoSchema(BaseModel):
    """应用信息返回字段"""
    id: int = Field(..., description="PostgreSQL 主键ID")
    app_id: str = Field(..., description="应用UUID，对应MongoDB中的app_id")
    name: str = Field(..., description="应用名称")
    description: Optional[str] = Field(None, description="应用描述")
    icon: Optional[str] = Field(None, description="图标emoji")
    type: str = Field(..., description="应用类型: workflow/ai/chat")
    is_public: bool = Field(..., description="是否公开分享")


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
