from dataclasses import dataclass

from langgraph.graph import StateGraph, START

from backend.app.common.core.core import tongyillm as model


@dataclass
class MyState:
    topic: str
    joke: str = ""




def call_model(state: MyState):
    """Call the LLM to generate a joke about a topic"""
    # Note that message events are emitted even when the LLM is run using .invoke rather than .stream
    model_response = model.stream(
        [
            {"role": "user", "content": f"Generate a story about {state.topic}"}
        ]
    )
    full_content = ""
    for chunk in model_response:
        content = chunk.content

        if content:
            # print(content,end="",flush=True)
            full_content += content
            yield {"joke": full_content}
    # return {"joke": model_response.content}

graph = (
    StateGraph(MyState)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .compile()
)

# The "messages" stream mode streams LLM tokens with metadata
# Use version="v2" for a unified StreamPart format
for chunk in graph.stream(
    {"topic": "小猫吃鱼"},
    stream_mode="messages",
    version="v2",
):
    print(chunk[0].content,end="",flush=True)