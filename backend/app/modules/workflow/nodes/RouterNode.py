
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import Field

from backend.app.common.core.logger import log

from backend.app.common.core.base_node import BaseNode
from backend.app.common.core.core import tongyillm as llm


class RouterNode(BaseNode):
    """条件路由节点

    根据用户输入让 LLM 选择一个分支，支持多分支条件路由
    """
    options: List[str] = Field(default_factory=list)
    llm: Any = Field(default=llm, description="大模型供应商")

    def __init__(self, **data):
        log.info(f"初始化RouterNode")
        super().__init__(**data)
        # 从 config 覆盖 options
        if "options" in self.config:
            self.options = self.config["options"]
        log.info(f"父类初始化完成，config={self.config}, options={self.options}")
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph会调用这个方法"""
        log.info(f"调用RouterNode，执行call方法")
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
            "node_id": self.id,
            "node_type": self.type,
            "decision": selected,
            "content": decision.content
        }

        # decision 字段用于路由判断，同时保存到 messages
        return {
            "messages": [message],
            "decision": selected
        }
