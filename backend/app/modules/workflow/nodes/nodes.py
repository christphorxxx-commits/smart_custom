# engine/nodes.py
from typing import Any, Dict, Iterator

from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.common.core.base_node import BaseNode
from backend.app.common.core.core import tongyillm as llm
from backend.app.modules.workflow.base_schema import Node


# ============ 类方式实现 ============
class LLMNode(BaseNode):
    def __init__(self, node: Node):
        self.node_id = node.id
        self.node_type = node.type
        self.config = node.config
        self.llm = llm

    def stream(self, state: Dict[str, Any]) -> Iterator[tuple[str, str]]:
        """为Token级流式输出生成每个token
        Yields (token, full_content_so_far)
        """
        prompt = self.config.get("prompt", "{input}")
        text = prompt.format(**state)
        full_content = ""
        for chunk in self.llm.stream(text):
            token = chunk.content
            if token:
                full_content += token
                yield token, full_content

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph会调用这个方法（普通模式）"""
        prompt = self.config.get("prompt", "{input}")
        text = prompt.format(**state)
        result = self.llm.invoke(text)
        content = result.content

        # 将当前节点输出追加到 messages 列表中
        message = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "content": content
        }

        # messages 使用 operator.add 会自动累加
        # 最后把最终结果放到 output
        return {
            "messages": [message],
            "output": content
        }


class RouterNode(BaseNode):
    def __init__(self, node: Node):
        self.node_id = node.id
        self.node_type = node.type
        self.config = node.config
        self.options = node.config["options"]
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph会调用这个方法"""
        system_prompt = f"根据用户输入选择一个类别: {self.options}"
        decision = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["input"])
        ])

        # 简化处理（生产建议用 structured output）
        selected = self.options[0]
        for opt in self.options:
            if opt in decision.content:
                selected = opt
                break

        # 将路由决策也保存到 messages
        message = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "decision": selected,
            "content": decision.content
        }

        # decision 字段用于路由判断，同时保存到 messages
        return {
            "messages": [message],
            "decision": selected
        }
