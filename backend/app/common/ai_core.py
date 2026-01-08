import asyncio
import os

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient




mcp_client = MultiServerMCPClient(
    {
    #     "math": {
    #         "transport": "stdio",  # Local subprocess communication
    #         "command": "python",
    #         # Absolute path to your math_server.py file
    #         "args": ["./math.py"],
    #     },
    #     "tavilySearch":{
    #         "transport": "stdio",
    #         "command": "python",
    #         "args": ["./fastMCP/tavilySearch.py"],
    #     },
    #     "gaodeMap":{
    #         "transport": "stdio",
    #         "command": "python",
    #         "args": ["./fastMCP/gaode.py"],
    #     },
    #     "amap-maps": {
    #         "transport": "stdio",
    #         "args": [
    #             "-y",
    #             "@amap/amap-maps-mcp-server"
    #             ],
    #         "command": "npx",
    #         "env": {
    #             "AMAP_MAPS_API_KEY": os.getenv("AMAP_MAPS_API_KEY"),
    #             }
    #         },
    #     "12306-mcp": {
    #         "transport": "stdio",
    #         "args": [
    #             "-y",
    #             "12306-mcp"
    #         ],
    #         "command": "npx"
    #     },
        # "mysql": {
        #     "transport": "stdio",
        #     "args": [
        #         "--directory",
        #         r"D:\anaconda\envs\hzy\Lib\site-packages\mysql_mcp_server",
        #         "run",
        #         "mysql_mcp_server"
        #     ],
        #     "command": "uv",
        #     "env": {
        #         "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE"),
        #         "MYSQL_HOST": os.getenv("MYSQL_HOST"),
        #         "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD"),
        #         "MYSQL_PORT": "3306",
        #         "MYSQL_USER": os.getenv("MYSQL_USER"),
        #     }
        # },
        # "redis": {
        #     "transport": "stdio",
        #     "command": "npx",
        #     "args": [
        #         "-y",
        #         "@modelcontextprotocol/server-redis",
        #         "redis://localhost:6379"
        #     ]
        # },
        "Bazi": {
            "transport": "stdio",
            "args": [
                "bazi-mcp"
            ],
            "command": "npx"
        }
        # "fetch": {
        #     "transport": "stdio",
        #     "command": "uvx",
        #     "args": ["mcp-server-fetch"]
        # },
        # "weather": {
        #     "transport": "http",  # HTTP-based remote server
        #     # Ensure you start your weather server on port 8000
        #     "url": "http://localhost:8000/mcp",
        # }
    }
)

tools = asyncio.run(mcp_client.get_tools())


#llm
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

llm = ChatOllama(
    model="qwen3:0.6b"
)

agent = create_agent(
    model=llm,
    tools=tools
)

async def userquery():
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content="帮我算一下我的八字，我是2000年农历9月23日出生的男生，时间大概是下午8点到9点")]}
    )
    # Extract structured content from tool messages
    for message in result["messages"]:
        print(message.content)
if __name__ == "__main__":
    asyncio.run(userquery())