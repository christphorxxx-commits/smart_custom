
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.common.core.base_node import BaseNode
from backend.app.common.core.core import tongyillm as llm
from backend.app.modules.workflow.schema import Node


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
