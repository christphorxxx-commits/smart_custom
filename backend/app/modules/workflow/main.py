# main.py
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到路径，允许直接运行
# 当前文件: backend/app/modules/app/main.py
# 项目根目录是: ../../../../.. => D:/pycharmWorkspace/smart_custom
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.modules.workflow.app import App


if __name__ == "__main__":
    # 读取默认的default.json配置
    default_json_path = Path(__file__).parent / "default.json"
    with open(default_json_path, "r", encoding="utf-8") as f:
        workflow_data = json.load(f)

    # 解析为App对象
    app = App.model_validate(workflow_data)

    # 使用默认输入运行，可以修改这里的输入测试不同内容
    user_input = "讲一个关于猫的故事"
    print(f"Running workflow with input: {user_input}")
    print("=" * 50)

    # Test 1: Original manual token streaming
    print("\n>>> Test 1: Manual Token Streaming")
    result = asyncio.run(app.run_and_stream_tokens(user_input))

    print("\n" + "=" * 50)
    print("\n>>> Test 2: Native LangGraph Token Streaming (stream_mode='messages')")
    # 使用原生LangGraph token级流式输出（每个token生成就输出）
    for token in app.stream_tokens_simple({"input": user_input}):
        print(token, end="", flush=True)
    print()  # Newline

    print("=" * 50)
    print("Final result:")
    print(result)
