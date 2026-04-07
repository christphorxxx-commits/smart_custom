import json
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, START, END

# ==========================================
# 1. 模拟数据库中的 JSON 配置 (The "Blueprint")
# ==========================================
# 这就是你保存 App 时，数据库里存的东西
# 注意：这里定义了 State 的字段 (schema) 和 图的逻辑 (graph)
APP_CONFIG_JSON = """
{
    "app_name": "RAG 助手",
    "schema": {
        "query": "str",
        "context": "str",
        "response": "str",
        "final_output": "str"
    },
    "nodes": [
        {
            "id": "start_node",
            "type": "start",
            "data": {}
        },
        {
            "id": "retrieval_node",
            "type": "retrieval",
            "data": {
                "mock_db": {
                    "苹果": "苹果是一种水果，富含维生素。",
                    "特斯拉": "特斯拉是一家电动汽车和清洁能源公司。"
                }
            }
        },
        {
            "id": "llm_node",
            "type": "llm",
            "data": {
                "system_prompt": "你是一个助手。",
                "user_template": "参考信息：{{context}}。请回答：{{query}}"
            }
        },
        {
            "id": "answer_node",
            "type": "answer",
            "data": {
                "output_key": "final_output",
                "source_key": "response"
            }
        }
    ],
    "edges": [
        {"source": "start_node", "target": "retrieval_node"},
        {"source": "retrieval_node", "target": "llm_node"},
        {"source": "llm_node", "target": "answer_node"}
    ]
}
"""


# ==========================================
# 2. 动态编译器 (The "Builder")
# ==========================================
class DynamicWorkflowCompiler:
    def __init__(self, config_json: str):
        self.config = json.loads(config_json)
        self.state_class = None
        self.builder = None

    def _create_dynamic_state_class(self):
        """
        核心黑科技：根据 JSON 里的 schema 字段，动态生成一个 TypedDict 类
        """
        schema = self.config.get("schema", {})
        # 将 JSON 的 "str" 映射到 Python 的 str 类型
        # 这里简单处理，实际可能需要映射 int, list 等
        annotations = {k: str for k, v in schema.items()}

        # 使用 type() 动态创建类
        # 相当于动态执行了: class DynamicState(TypedDict): query: str; context: str...
        self.state_class = type("DynamicState", (TypedDict,), {"__annotations__": annotations})
        print(f"⚙️ [编译] 动态生成 State 类，字段: {list(annotations.keys())}")

    def _get_node_function(self, node_conf: Dict):
        """
        工厂模式：根据节点类型和配置，返回一个可调用的函数
        """
        node_type = node_conf["type"]
        node_id = node_conf["id"]
        data = node_conf.get("data", {})

        # --- 定义具体的节点逻辑 ---

        def start_logic(state):
            print(f"   [运行] 节点({node_id}): 接收输入 -> {state.get('query')}")
            return {}

        def retrieval_logic(state):
            query = state.get("query")
            # 模拟检索：从配置里拿 mock_db
            mock_db = data.get("mock_db", {})
            context = mock_db.get(query, f"未找到关于 '{query}' 的信息。")
            print(f"   [运行] 节点({node_id}): 检索到 -> {context}")
            return {"context": context}

        def llm_logic(state):
            # 模拟变量替换：把 {{query}} 替换成 state['query']
            prompt_template = data.get("user_template")
            # 简单替换逻辑
            final_prompt = prompt_template.replace("{{query}}", state.get("query", "")).replace("{{context}}",
                                                                                                state.get("context",
                                                                                                          ""))

            # 模拟 LLM 输出
            llm_result = f"(LLM模拟回复) 基于 '{state.get('context')}'，我回答：{state.get('query')}"
            print(f"   [运行] 节点({node_id}): 生成回复 -> {llm_result}")
            return {"response": llm_result}

        def answer_logic(state):
            source = data.get("source_key")
            target = data.get("output_key")
            # 搬运数据
            result = state.get(source)
            print(f"   [运行] 节点({node_id}): 输出 -> {result}")
            return {target: result}

        # --- 路由分发 ---
        if node_type == "start":
            return start_logic
        elif node_type == "retrieval":
            return retrieval_logic
        elif node_type == "llm":
            return llm_logic
        elif node_type == "answer":
            return answer_logic
        else:
            raise ValueError(f"未知节点类型: {node_type}")

    def compile(self) -> Any:
        """
        编译：读取 JSON -> 构建 LangGraph -> 返回可运行的 App
        """
        print("\n🚀 开始编译工作流...")

        # 1. 生成 State 类
        self._create_dynamic_state_class()

        # 2. 初始化图
        self.builder = StateGraph(self.state_class)

        # 3. 添加节点
        for node_conf in self.config["nodes"]:
            func = self._get_node_function(node_conf)
            self.builder.add_node(node_conf["id"], func)
            print(f"   [编译] 添加节点: {node_conf['id']} ({node_conf['type']})")

        # 4. 添加边
        for edge in self.config["edges"]:
            self.builder.add_edge(edge["source"], edge["target"])
            print(f"   [编译] 连线: {edge['source']} -> {edge['target']}")

        # 5. 设置入口和出口
        self.builder.add_edge(START, self.config["nodes"][0]["id"])  # 假设第一个是入口
        self.builder.add_edge(self.config["nodes"][-1]["id"], END)  # 假设最后一个是出口

        # 6. 编译成 runnable
        print("✅ 编译完成！\n")
        return self.builder.compile()


# ==========================================
# 3. 运行与测试
# ==========================================

if __name__ == "__main__":
    # 1. 实例化编译器（加载配置）
    compiler = DynamicWorkflowCompiler(APP_CONFIG_JSON)

    # 2. 编译出 App
    app = compiler.compile()

    # 3. 准备初始 State (必须包含 schema 里定义的 query)
    # 注意：这里我们不需要知道 State 具体长啥样，编译器已经帮我们处理好了
    initial_inputs = {"query": "特斯拉"}

    # 4. 运行
    print("-" * 30)
    print("▶️ 开始运行 App")
    final_state = app.invoke(initial_inputs)
    print("-" * 30)

    # 5. 获取结果
    print(f"\n🎉 最终结果: {final_state.get('final_output')}")