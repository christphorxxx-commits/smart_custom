from langchain.agents import create_agent
import os

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.agents.middleware import wrap_model_call,ModelRequest,ModelResponse

advanced_model = ChatOpenAI(
    model="Qwen/Qwen3-Next-80B-A3B-Thinking",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_URL"),
    temperature=0.7,
    streaming=True,
)

basic_model = ChatOllama(
    model="qwen3:0.6b"
)

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """根据对话复杂性选择模型"""
    message_count = len(request.messages)
    if message_count > 10:
        #使用一个先进模型用于长对话
        model = advanced_model
    else:
        model = basic_model

    return handler(request.override(model=model))

@wrap_model_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Tool error: Please check your input and try again.({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


@tool
def search(query: str)->str:
    """Search for information"""
    return f"Results for: {query}"

@tool
def get_weather(location: str)->str:
    """Get weather information  for a location"""
    return f"Weather in {location}: Sunny, 72°F"

agent = create_agent(
    model=basic_model,
    tools=[search,get_weather],
    middleware=[dynamic_model_selection]
)

