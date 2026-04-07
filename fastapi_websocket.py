from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END


# ==========================================
# 1. 定义“内存” (State)
# ==========================================
# 这就是我们之前用的 graph_context 字典，但在 LangGraph 中需要定义类型
class WorkflowState(TypedDict):
    query: str  # 用户输入
    translation_result: str  # 第一个 LLM 的输出
    polish_result: str  # 第二个 LLM 的输出
    final_answer: str  # 最终结果


# ==========================================
# 2. 定义“节点” (Nodes)
# ==========================================
# 在 LangGraph 中，节点就是函数。
# 它们接收当前的 State，并返回需要更新的字段。

def start_node(state: WorkflowState) -> Dict:
    """
    开始节点：只负责接收输入
    注意：这里我们模拟从外部传入 query
    """
    print(f"   [Start] 接收输入: {state['query']}")
    return {}  # Start 节点通常不需要更新 state，因为 query 已经在里面了


def llm_translator_node(state: WorkflowState) -> Dict:
    """
    LLM 节点 A：翻译
    """
    print(f"   [LLM A: Translator] 正在翻译: '{state['query']}'...")
    # 模拟 LLM 逻辑：把中文变成英文
    translated_text = f"(Translated) {state['query']} in English"

    # 返回更新指令：更新 translation_result 字段
    return {"translation_result": translated_text}


def llm_polisher_node(state: WorkflowState) -> Dict:
    """
    LLM 节点 B：润色
    """
    print(f"   [LLM B: Polisher] 正在润色: '{state['translation_result']}'...")
    # 模拟 LLM 逻辑：把简单的英文变成高级英文
    polished_text = f"(Polished) {state['translation_result']} - sounds professional!"

    # 返回更新指令：更新 polish_result 字段
    return {"polish_result": polished_text}


def answer_node(state: WorkflowState) -> Dict:
    """
    输出节点：整理最终结果
    """
    final_text = f"最终答案: {state['polish_result']}"
    print(f"   [Answer] 输出: {final_text}")
    return {"final_answer": final_text}


# ==========================================
# 3. 构建“工作流图” (The Graph)
# ==========================================
# 这就是我们的“引擎”和“连线”配置

# 1. 初始化图，告诉它我们使用哪种 State
builder = StateGraph(WorkflowState)

# 2. 添加节点
# 格式：builder.add_node("唯一ID", 对应的函数)
builder.add_node("start", start_node)
builder.add_node("translator", llm_translator_node)
builder.add_node("polisher", llm_polisher_node)
builder.add_node("answer", answer_node)

# 3. 添加边 (Edges) - 定义流转逻辑
# 设置入口点：图从 "start" 开始
builder.set_entry_point("start")

# 顺序连接：Start -> Translator -> Polisher -> Answer
builder.add_edge("start", "translator")
builder.add_edge("translator", "polisher")
builder.add_edge("polisher", "answer")

# 结束：Answer 节点执行完后，流向 END (结束)
builder.add_edge("answer", END)

# 4. 编译图
# 这一步相当于“实例化引擎”，准备好运行
workflow_app = builder.compile()

# ==========================================
# 4. 运行与调试
# ==========================================

# 模拟用户输入
initial_state = {
    "query": "你好世界",
    "translation_result": "",
    "polish_result": "",
    "final_answer": ""
}

print("🚀 开始运行 LangGraph 工作流...")
print("-" * 30)

# 调用 invoke 方法，传入初始状态
# LangGraph 会自动根据图结构，依次调用节点函数，并合并 State
final_state = workflow_app.invoke(initial_state)

print("-" * 30)
print("✅ 执行完毕")
print(f"🎯 最终结果: {final_state['final_answer']}")