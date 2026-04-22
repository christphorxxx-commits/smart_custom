import operator
from typing import Dict, Any, Optional, TypedDict, Annotated

from pydantic import Field, BaseModel

from backend.app.common.enums import EdgeTypeEnum
from backend.app.common.enums import NodeEnum


class BaseNode(BaseModel):
    id: str = Field(..., description="ID")
    x: Optional[float] = Field(None, description="节点X坐标（画布位置）")
    y: Optional[float] = Field(None, description="节点Y坐标（画布位置）")
    name: Optional[str] = Field(None, description="节点名称")
    config: Optional[Dict[str, Any]] = Field(..., description="节点配置")
    description: Optional[str] = Field(default="这是一个node", description="节点描述")
    type: NodeEnum = Field(..., description="节点类型")

    model_config = {
        "arbitrary_types_allowed": True
    }



class Edge(BaseModel):
    """工作流边模型"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    type: EdgeTypeEnum = Field(..., description="边类型")
    condition: str | None = Field(default=None, description="条件表达式（router节点专用）")

#total=False标识允许额外字段，也就是新的字段
class State(TypedDict, total=False):
    input: str  # 用户输入（只读）
    messages: Annotated[list, operator.add]  # 对话上下文（累加）
    variables: Annotated[dict, lambda old, new: {**old, **new}]  # 节点输出（按节点存储）- 合并字典
    decision: Annotated[str, lambda old, new: new]  # 路由决策（用新值覆盖旧值）
    output: Annotated[str, lambda old, new: new]  # 最终输出（用新值覆盖旧值）
