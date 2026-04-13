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


class AppInfoQuerySchema(BaseModel):
    """请求字段"""
    id: int
    app_id: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    type: str
    is_public: bool

class AppInfoSchema(BaseModel):
    """app信息返回字段"""

