from typing import Any, Iterator, AsyncIterator, Dict, Optional, List

from langgraph.graph import StateGraph, START, END
from pydantic import Field, BaseModel

from backend.app.common.utils.common_util import uuid4_str
from backend.app.modules.workflow.base_schema import State, Node, Edge
from backend.app.modules.workflow.nodes.nodes import LLMNode, RouterNode


class App(BaseModel):
    app_id: str
    nodes: List[Node]
    edges: List[Edge]
    # 缓存已创建的node实例，避免重复构建，exclude=True不让Pydantic序列化它
    node_instances: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    # 初始化/之前必须按照位置传递（仅位置参数），之后**data必须作为关键字参数传递
    def __init__(self, /, **data: Any):
        if 'app_id' not in data:
            data['app_id'] = uuid4_str()
        super().__init__(**data)
        # 预构建所有node实例，分层清晰：App持有node实例
        self._build_node_instances()

    def _build_node_instances(self):
        """预构建所有node实例，具体执行逻辑由node自己提供"""
        for node_def in self.nodes:
            if node_def.type == "llm":
                self.node_instances[node_def.id] = LLMNode(node_def)
            elif node_def.type == "router":
                self.node_instances[node_def.id] = RouterNode(node_def)
            else:
                # start/end 不需要实例
                self.node_instances[node_def.id] = None

    def compile(self):
        graph = StateGraph(State)

        # 1️⃣ 创建节点
        for node in self.nodes:
            if node.type == "llm":
                current_node = LLMNode(node)
            elif node.type == "router":
                current_node = RouterNode(node)
            else:
                # start/end 不需要实际节点，由框架处理
                current_node = lambda x: x

            graph.add_node(node.id, current_node)

        # 2️⃣ 添加边
        for edge in self.edges:
            if edge.type == "normal":
                if edge.source == "start":
                    graph.add_edge(START, edge.target)
                elif edge.target == "end":
                    graph.add_edge(edge.source, END)
                else:
                    graph.add_edge(edge.source, edge.target)

        # 3️⃣ 处理 conditional edges
        router_nodes = [n for n in self.nodes if n.type == "router"]

        for router in router_nodes:
            def route_fn(state):
                return state.get("decision")

            mapping = {
                edge.condition: edge.target
                for edge in self.edges
                if edge.source == router.id and edge.type == "conditional"
            }

            graph.add_conditional_edges(router.id, route_fn, mapping)

        return graph.compile()

    def run(self, input_data: dict):
        """直接运行工作流，返回最终结果"""
        graph = self.compile()
        return graph.invoke(input_data)

    def stream(self, input_data: dict):
        """流式输出工作流，按节点返回（每个节点完成后输出一次）"""
        graph = self.compile()
        for chunk in graph.stream(input_data):
            yield chunk

    async def astream(self, input_data: dict):
        """异步流式输出，按节点返回"""
        graph = self.compile()
        async for chunk in graph.astream(input_data):
            yield chunk

    async def run_and_stream(self, input_str: str):
        """直接运行工作流并流式输出到控制台"""
        result = []
        for chunk in self.stream({"input": input_str}):
            result.append(chunk)
            print(chunk)
        return {"result": result}

    # ============ Token级流式输出 ============
    def _get_next_node(self, current_node_id: str) -> str | None:
        """根据当前节点获取下一个普通节点"""
        for edge in self.edges:
            if edge.source == current_node_id and edge.type == "normal" and edge.target != "end":
                return edge.target
        return None

    def _get_next_node_after_router(self, current_node_id: str, decision: str) -> str | None:
        """根据路由决策获取下一个节点"""
        for edge in self.edges:
            if edge.source == current_node_id and edge.type == "conditional" and edge.condition == decision:
                return edge.target
        # 如果没找到匹配，回退到第一个normal边
        for edge in self.edges:
            if edge.source == current_node_id and edge.type == "normal":
                return edge.target
        return None

    def _get_start_node(self) -> str | None:
        """获取起始节点（start指向的第一个节点）"""
        for edge in self.edges:
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

            if node_def.type == "llm":
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
                    "node_id": node_instance.node_id,
                    "node_type": node_instance.node_type,
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

            elif node_def.type == "router":
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

            else:
                # 其他节点，直接继续
                current_node_id = self._get_next_node(current_node_id)

        yield {
            "type": "workflow_complete",
            "final_output": current_state.get("output", ""),
            "final_state": current_state
        }

    def _get_node_def(self, node_id: str) -> Optional[Node]:
        """根据node_id获取node定义"""
        return next((n for n in self.nodes if n.id == node_id), None)

    async def astream_tokens(self, input_data: dict) -> AsyncIterator[Dict[str, Any]]:
        """异步Token级流式输出，用于FastAPI WebSocket"""
        import asyncio
        for event in self.stream_tokens(input_data):
            yield event
            await asyncio.sleep(0)

    async def run_and_stream_tokens(self, input_str: str):
        """直接运行工作流并Token级流式输出到控制台"""
        result = ""
        for event in self.stream_tokens({"input": input_str}):
            if event["type"] == "token":
                print(event["token"], end="", flush=True)
                result = event["full_content"]
        print()  # 换行
        return {"result": result}

    # ============ Native LangGraph Token-level Streaming (using stream_mode="messages") ============
    def stream_tokens_native(self, input_data: dict) -> Iterator[Any]:
        """
        Token-level streaming using LangGraph's native stream_mode="messages"
        Yields each token as it's generated from the LLM directly
        """
        graph = self.compile()
        for chunk in graph.stream(input_data, stream_mode="messages"):
            yield chunk

    async def astream_tokens_native(self, input_data: dict) -> AsyncIterator[Any]:
        """
        Async token-level streaming using LangGraph's native stream_mode="messages"
        For FastAPI WebSocket usage
        """
        graph = self.compile()
        async for chunk in graph.astream(input_data, stream_mode="messages"):
            yield chunk

    def stream_tokens_simple(self, input_data: dict) -> Iterator[str]:
        """Simple token streaming that yields token content directly"""
        graph = self.compile()
        for msg, metadata in graph.stream(input_data, stream_mode="messages"):
            if msg.content:
                yield msg.content

    async def astream_tokens_simple(self, input_data: dict) -> AsyncIterator[str]:
        """Async simple token streaming that yields token content directly"""
        graph = self.compile()
        async for msg, metadata in graph.astream(input_data, stream_mode="messages"):
            if msg.content:
                yield msg.content