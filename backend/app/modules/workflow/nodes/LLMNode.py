from typing import Dict, Any, Iterator, AsyncGenerator

from pydantic import Field

from backend.app.common.core.base_node import BaseNode
from backend.app.common.core.core import tongyillm


# ============ 类方式实现 ============
from typing import Any

class LLMNode(BaseNode):
    """LLM 生成节点

    调用大模型生成文本，支持 Token 级流式输出
    """
    llm: Any = Field(default=tongyillm,description="大模型供应商")

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = tongyillm

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

    async def astream(self, state: Dict[str, Any]) -> AsyncGenerator[tuple[Any, str], Any]:
        """为Token级流式输出生成每个token
        Yields (token, full_content_so_far)
        """
        prompt = self.config.get("prompt", "{input}")
        text = prompt.format(**state)
        full_content = ""
        for chunk in self.llm.astream(text):
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
            "node_id": self.id,
            "node_type": self.type,
            "content": content
        }

        # messages 使用 operator.add 会自动累加
        # 最后把最终结果放到 output
        return {
            "messages": [message],
            "output": content
        }
