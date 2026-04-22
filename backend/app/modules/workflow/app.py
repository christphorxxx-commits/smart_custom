from typing import Any, Iterator, AsyncIterator, Dict, Optional, List

from langgraph.graph import StateGraph, START, END
from pydantic import Field, BaseModel

from backend.app.common.core.base_node import State, Edge, BaseNode
from backend.app.common.utils.common_util import uuid4_str
from backend.app.modules.workflow.nodes.LLMNode import LLMNode
from backend.app.modules.workflow.nodes.RetrieveNode import RetrieveNode
from backend.app.modules.workflow.nodes.RouterNode import RouterNode
from backend.app.common.enums import NodeEnum, EdgeTypeEnum


class App(BaseModel):
    uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: List[Dict[str, Any]]  # MongoDB 存储的原始字典
    edges: List[Dict[str, Any]]  # MongoDB 存储的原始字典

    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow"
    }
    # 初始化/之前必须按照位置传递（仅位置参数），之后**data必须作为关键字参数传递
    def __init__(self, /, **data: Any):
        if 'uuid' not in data:
            data['uuid'] = uuid4_str()
        super().__init__(**data)
        # 动态创建，不声明为类字段，避免Pydantic验证node_instances里的实例
        self._parsed_nodes: List[BaseNode] = []
        self._parsed_edges: List[Edge] = []
        self.node_instances: Dict[str, Any] = {}
        self._parse_nodes_and_edges()
        # 预构建所有node实例，分层清晰：App持有node实例
        self._build_node_instances()

    def _parse_nodes_and_edges(self):
        """将原始字典解析为 BaseNode 和 Edge"""
        from backend.app.common.enums import NodeEnum
        # 解析 nodes
        self._parsed_nodes = []
        for node_dict in self.nodes:
            # 确保 node_dict 是字典
            if not isinstance(node_dict, dict) and hasattr(node_dict, 'model_dump'):
                node_dict = node_dict.model_dump()
            node = BaseNode(**node_dict)
            self._parsed_nodes.append(node)
        # 解析 edges
        self._parsed_edges = []
        for edge_dict in self.edges:
            if not isinstance(edge_dict, dict) and hasattr(edge_dict, 'model_dump'):
                edge_dict = edge_dict.model_dump()
            edge = Edge(**edge_dict)
            self._parsed_edges.append(edge)

    def _build_node_instances(self):
        """预构建所有node实例，具体执行逻辑由node自己提供"""
        for node_def in self._parsed_nodes:
            node_data = node_def.model_dump()
            node_type = node_def.type.value if hasattr(node_def.type, 'value') else node_def.type
            if node_type == NodeEnum.LLM.value:
                self.node_instances[node_def.id] = LLMNode(**node_data)
            elif node_type == NodeEnum.ROUTE.value:
                self.node_instances[node_def.id] = RouterNode(**node_data)
            elif node_type == NodeEnum.RETRIEVE.value:
                self.node_instances[node_def.id] = RetrieveNode(**node_data)
            else:
                # start/end 不需要实例
                self.node_instances[node_def.id] = None

    def compile(self):
        from backend.app.common.enums import NodeEnum
        graph = StateGraph(State)

        # 1️⃣ 创建节点
        for node in self._parsed_nodes:
            node_data = node.model_dump()
            node_type = node.type.value if hasattr(node.type, 'value') else node.type
            if node_type == NodeEnum.LLM.value:
                current_node = LLMNode(**node_data)
            elif node_type == NodeEnum.ROUTE.value:
                current_node = RouterNode(**node_data)
            elif node_type == NodeEnum.RETRIEVE.value:
                current_node = RetrieveNode(**node_data)
            else:
                # start/end 不需要实际节点，由框架处理
                current_node = lambda x: x

            graph.add_node(node.id, current_node)

        # 2️⃣ 添加边
        for edge in self._parsed_edges:
            edge_type = edge.type.value if hasattr(edge.type, 'value') else edge.type
            if edge_type == EdgeTypeEnum.NORMAL.value:
                if edge.source == "start":
                    graph.add_edge(START, edge.target)
                elif edge.target == "end":
                    graph.add_edge(edge.source, END)
                else:
                    graph.add_edge(edge.source, edge.target)

        # 3️⃣ 处理 conditional edges
        router_nodes = [n for n in self._parsed_nodes if (n.type.value if hasattr(n.type, 'value') else n.type) == NodeEnum.ROUTE.value]

        for router in router_nodes:
            def route_fn(state):
                return state.get("decision")

            mapping = {
                edge.condition: edge.target
                for edge in self._parsed_edges
                if edge.source == router.id and (edge.type.value if hasattr(edge.type, 'value') else edge.type) == EdgeTypeEnum.CONDITIONAL.value
            }

            graph.add_conditional_edges(router.id, route_fn, mapping)

        return graph.compile()

    async def astream(self, input_data: dict):
        """异步流式输出，按节点返回"""
        graph = self.compile()
        async for chunk in graph.astream(input_data):
            yield chunk

    # ============ Token级流式输出 ============
    def _get_next_node(self, current_node_id: str) -> str | None:
        """根据当前节点获取下一个普通节点"""
        from backend.app.common.enums import EdgeTypeEnum
        for edge in self._parsed_edges:
            edge_type = edge.type.value if hasattr(edge.type, 'value') else edge.type
            if edge.source == current_node_id and edge_type == EdgeTypeEnum.NORMAL.value and edge.target != "end":
                return edge.target
        return None

    def _get_next_node_after_router(self, current_node_id: str, decision: str) -> str | None:
        """根据路由决策获取下一个节点"""
        for edge in self._parsed_edges:
            edge_type = edge.type.value if hasattr(edge.type, 'value') else edge.type
            if edge.source == current_node_id and edge_type == EdgeTypeEnum.CONDITIONAL.value and edge.condition == decision:
                return edge.target
        # 如果没找到匹配，回退到第一个normal边
        for edge in self._parsed_edges:
            edge_type = edge.type.value if hasattr(edge.type, 'value') else edge.type
            if edge.source == current_node_id and edge_type == EdgeTypeEnum.NORMAL.value:
                return edge.target
        return None

    def _get_start_node(self) -> str | None:
        """获取起始节点（start指向的第一个节点）"""
        for edge in self._parsed_edges:
            if edge.source == "start":
                return edge.target
        return None

    def stream_tokens(self, input_data: dict) -> Iterator[Dict[str, Any]]:
        """
        Token级流式输出 - 每个LLM token生成就输出
        App负责流程控制，具体执行由node完成
        """
        current_state: State = input_data.copy()
        current_state.setdefault("messages", [])
        current_state.setdefault("variables", {})

        current_node_id = self._get_start_node()

        while current_node_id is not None:
            node_def = self._get_node_def(current_node_id)
            if node_def is None:
                break

            node_instance = self.node_instances.get(current_node_id)

            node_type = node_def.type.value if hasattr(node_def.type, 'value') else node_def.type
            if node_type == NodeEnum.LLM.value:
                # LLM节点：调用node.stream()逐个获取token
                full_content = ""
                for (token, full_content) in node_instance.stream(current_state):
                    yield {
                        "type": "token",
                        "token": token,
                        "full_content": full_content,
                        "node_id": current_node_id
                    }

                # 节点完成，App负责更新整体状态
                message = {
                    "node_id": node_def.id,
                    "node_type": node_def.type.value if hasattr(node_def.type, 'value') else node_def.type,
                    "content": full_content
                }
                update = {
                    "messages": [message],
                    "output": full_content,
                    "variables": {
                        **current_state.get("variables", {}),
                        node_def.id: full_content
                    }
                }
                current_state.update(update)
                yield {
                    "type": "node_complete",
                    "node_id": current_node_id,
                    "output": update
                }

                # 获取下一个节点（App负责流程控制）
                current_node_id = self._get_next_node(current_node_id)

            node_type = node_def.type.value if hasattr(node_def.type, 'value') else node_def.type
            if node_type == NodeEnum.ROUTE.value:
                # 路由节点：调用node.__call__获取决策
                update = node_instance(current_state)
                current_state.update(update)
                decision = current_state.get("decision")
                yield {
                    "type": "node_complete",
                    "node_id": current_node_id,
                    "output": update
                }
                # 根据决策找下一个节点（App负责流程控制）
                current_node_id = self._get_next_node_after_router(current_node_id, decision)

            elif node_type == NodeEnum.RETRIEVE.value:
                # 知识库检索节点：调用node.__call__检索文档
                update = node_instance(current_state)
                current_state.update(update)
                yield {
                    "type": "node_complete",
                    "node_id": current_node_id,
                    "output": update
                }
                # 获取下一个节点（App负责流程控制）
                current_node_id = self._get_next_node(current_node_id)

            else:
                # 其他节点，直接继续
                current_node_id = self._get_next_node(current_node_id)

        yield {
            "type": "workflow_complete",
            "final_output": current_state.get("output", ""),
            "final_state": current_state
        }

    def _get_node_def(self, node_id: str) -> Optional[BaseNode]:
        """根据node_id获取node定义"""
        return next((n for n in self._parsed_nodes if n.id == node_id), None)

    async def astream_tokens(self, input_data: dict) -> AsyncIterator[Dict[str, Any]]:
        """异步Token级流式输出，用于FastAPI WebSocket"""
        import asyncio
        for event in self.stream_tokens(input_data):
            yield event
            await asyncio.sleep(0)
