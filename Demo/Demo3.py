import os
from typing import Literal, Annotated

# LangChain 核心组件
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessageChunk, AIMessage

# LangGraph 组件
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# --- 1. 设置 API Key (请替换为你的 Key 或设置环境变量) ---


# 如果使用国内中转 API，请设置 base_url
# os.environ["OPENAI_API_BASE_URL"] = "https://api.example.com/v1"

# --- 2. 定义状态 (State) ---
# 我们使用简单的字典来存储消息历史
class State(dict):
    messages: Annotated[list, add_messages]


# --- 3. 定义工具 (用于路由判断) ---
# 让 LLM 通过调用工具来决定走哪条路，比纯文本分类更稳定
def write_poem(topic: str):
    """写一首关于特定主题的诗。"""
    return f"准备写关于 {topic} 的诗"


def write_story(topic: str):
    """写一个关于特定主题的故事。"""
    return f"准备写关于 {topic} 的故事"


def tell_joke():
    """讲一个笑话。"""
    return "准备讲一个笑话"


# --- 4. 定义节点函数 ---
from backend.app.common.core.core import tongyillm
# 初始化 LLM (绑定工具用于路由)
llm_with_tools = tongyillm.bind_tools([write_poem, write_story, tell_joke])
# 初始化纯 LLM (用于生成内容)
llm_generator = tongyillm


def router_node(state: State):
    """路由节点：根据用户输入决定调用哪个工具"""
    messages = state["messages"]
    # 这里我们让 LLM 自己决定调用哪个工具
    # 注意：这里只是做决策，不生成最终内容
    response = llm_with_tools.invoke(messages)

    # 将决策结果（工具调用）加入消息历史，以便后续节点知道该干嘛
    # 但为了演示简单，我们直接把工具调用结果作为状态传递
    return {"tool_calls": response.tool_calls}


def poem_node(state: State):
    """写诗节点"""
    print("\n🤖 [系统]: 正在为您写诗...")
    topic = state["messages"][-1].content  # 简单获取用户输入作为主题
    prompt = f"请写一首关于 '{topic}' 的短诗。"

    # 流式生成
    for chunk in llm_generator.stream(prompt):
        yield {"messages": [chunk]}


def story_node(state: State):
    """写故事节点"""
    print("\n🤖 [系统]: 正在为您编故事...")
    topic = state["messages"][-1].content
    prompt = f"请讲一个关于 '{topic}' 的短故事。"

    # 流式生成
    for chunk in llm_generator.stream(prompt):
        yield {"messages": [chunk]}


def joke_node(state: State):
    """讲笑话节点"""
    print("\n🤖 [系统]: 正在为您讲笑话...")
    prompt = "请讲一个好笑的中文笑话。"

    # 流式生成
    for chunk in llm_generator.stream(prompt):
        yield {"messages": [chunk]}


# --- 5. 定义路由逻辑 ---

def route_logic(state: State):
    """根据工具调用结果分发到不同节点"""
    tool_calls = state.get("tool_calls", [])

    if not tool_calls:
        return "joke_node"  # 默认 fallback

    tool_name = tool_calls[0]["name"]

    if tool_name == "write_poem":
        return "poem_node"
    elif tool_name == "write_story":
        return "story_node"
    elif tool_name == "tell_joke":
        return "joke_node"
    else:
        return "joke_node"


# --- 6. 构建图 ---

builder = StateGraph(State)

# 添加节点
builder.add_node("router", router_node)
builder.add_node("poem_node", poem_node)
builder.add_node("story_node", story_node)
builder.add_node("joke_node", joke_node)

# 设置入口
builder.set_entry_point("router")

# 添加条件边 (路由)
builder.add_conditional_edges(
    "router",
    route_logic,
    {
        "poem_node": "poem_node",
        "story_node": "story_node",
        "joke_node": "joke_node"
    }
)

# 所有节点结束后退出
builder.add_edge("poem_node", END)
builder.add_edge("story_node", END)
builder.add_edge("joke_node", END)

# 编译图
app = builder.compile()


# --- 7. 运行并流式输出 ---

def run_chat():
    print("👋 你好！我是智能助手。我可以写诗、写故事或讲笑话。")

    while True:
        user_input = input("\n👤 请输入 (输入 'quit' 退出): ")
        if user_input.lower() == 'quit':
            break

        # 构建初始状态
        inputs = {"messages": [HumanMessage(content=user_input)]}

        print("\n--- 开始流式输出 ---")

        # 使用 stream 模式
        # stream_mode="messages" 会直接输出 LLM 生成的文本块
        for chunk in app.stream(inputs, stream_mode="messages"):
            # chunk 是 AIMessageChunk 对象
            if isinstance(chunk, AIMessage):
                # 打印内容，end="" 防止换行，flush=True 立即刷新缓冲区
                print(chunk,end="", flush=True)

        print("\n--- 输出结束 ---")


if __name__ == "__main__":
    run_chat()