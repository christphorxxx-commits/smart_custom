{
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "x": 100,
      "y": 150,
      "data": {
        "title": "开始"
      }
    },
    {
      "id": "router",
      "type": "if",
      "x": 400,
      "y": 150,
      "data": {
        "title": "条件路由",
        "options": [
          "story",
          "joke",
          "poem"
        ]
      }
    },
    {
      "id": "story_node",
      "type": "llm",
      "x": 717.0379746835443,
      "y": 12.936708860759492,
      "data": {
        "title": "大模型",
        "prompt": "写一个故事：{input}",
        "model": "gpt-4o"
      }
    },
    {
      "id": "joke_node",
      "type": "llm",
      "x": 702,
      "y": 382,
      "data": {
        "title": "大模型",
        "prompt": "讲一个笑话：{input}"
      }
    },
    {
      "id": "poem_node",
      "type": "llm",
      "x": 728.9203276247207,
      "y": 164.92181682799702,
      "data": {
        "title": "大模型",
        "prompt": "写一首诗：{input}"
      }
    },
    {
      "id": "end",
      "type": "endpoint",
      "x": 1139.240506329114,
      "y": 150,
      "data": {
        "title": "结束"
      }
    }
  ],
  "connections": [
    {
      "id": "conn_0",
      "sourceNodeId": "start",
      "sourcePort": "output",
      "targetNodeId": "router",
      "targetPort": "input"
    },
    {
      "id": "conn_1",
      "sourceNodeId": "router",
      "sourcePort": "output",
      "targetNodeId": "story_node",
      "targetPort": "input"
    },
    {
      "id": "conn_2",
      "sourceNodeId": "router",
      "sourcePort": "output",
      "targetNodeId": "joke_node",
      "targetPort": "input"
    },
    {
      "id": "conn_3",
      "sourceNodeId": "router",
      "sourcePort": "output",
      "targetNodeId": "poem_node",
      "targetPort": "input"
    },
    {
      "id": "conn_4",
      "sourceNodeId": "story_node",
      "sourcePort": "output",
      "targetNodeId": "end",
      "targetPort": "input"
    },
    {
      "id": "conn_5",
      "sourceNodeId": "joke_node",
      "sourcePort": "output",
      "targetNodeId": "end",
      "targetPort": "input"
    },
    {
      "id": "conn_6",
      "sourceNodeId": "poem_node",
      "sourcePort": "output",
      "targetNodeId": "end",
      "targetPort": "input"
    }
  ],
  "version": 1
}