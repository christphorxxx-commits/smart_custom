from typing import Literal, Dict, Any, List, TypedDict, Annotated
import operator
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END


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


class Workflow(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
