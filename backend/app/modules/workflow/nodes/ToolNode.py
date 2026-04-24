"""
工具调用节点 - ToolNode
支持调用自定义工具（Python函数），可以配置工具参数和名称

预设工具（内置可直接使用）：
- http_get: 发送 HTTP GET 请求
- http_post: 发送 HTTP POST 请求
- calculator: 计算器（加减乘除）
- get_current_time: 获取当前时间
- json_parse: 解析 JSON 字符串
"""
import json
from enum import Enum
from typing import Dict, Any, Callable, Optional, Iterator, AsyncGenerator, Literal, List

from pydantic import BaseModel, Field

from backend.app.common.core.base_node import BaseNode
from backend.app.common.core.logger import log
from backend.app.config.setting import settings


# ============ 配置字段常量枚举 ============
class ToolNodeConfigFields(str, Enum):
    """ToolNode 配置字段名称枚举"""
    TOOL_NAME = "tool_name"
    TOOL_DESCRIPTION = "tool_description"
    PARAMETERS = "parameters"
    PYTHON_CODE = "python_code"
    INPUT_MAPPING = "input_mapping"
    OUTPUT_KEY = "output_key"

    @classmethod
    def all_fields(cls) -> List[str]:
        return [field.value for field in cls]


# ============ Pydantic 配置模型 - 明确定义ToolNode.config所有字段 ============
class ToolParameterDef(BaseModel):
    """工具参数定义"""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型: string/int/float/boolean/object")
    description: str = Field("", description="参数功能描述")
    required: bool = Field(False, description="是否必填")
    default: Optional[Any] = Field(None, description="默认值")


class ToolNodeConfig(BaseModel):
    """ToolNode 配置项定义"""
    tool_name: str = Field(..., description="工具名称，必须与注册表中注册的名称一致")
    tool_description: str = Field("", description="工具功能描述，用于前端展示和LLM理解")
    parameters: List[ToolParameterDef] = Field(default_factory=list, description="参数定义列表")
    python_code: Optional[str] = Field(None, description="自定义工具Python代码，必须定义tool_func(**params)")
    input_mapping: Dict[str, str] = Field(default_factory=dict, description="输入映射: {参数名: state变量名}")
    output_key: str = Field("tool_output", description="结果保存到state的key名称")


# 全局注册表 - 所有已注册的工具（放在类外面，避免Pydantic处理）
_tool_registry: Dict[str, Callable] = {}


class ToolNode(BaseNode):
    """工具调用节点

    配置项 (config):
    - tool_name: str 工具名称（选择预设工具直接写名称）
    - tool_description: str 工具描述
    - parameters: List[Dict] 参数定义
        [
            {
                "name": "param_name",
                "type": "string/int/boolean",
                "description": "参数说明",
                "required": true/false,
                "default": 默认值
            }
        ]
    - python_code: str 自定义Python代码（自定义工具时填写）
    - input_mapping: Dict 输入映射，将 state 中的变量映射到工具参数
        {"param_name": "state_variable_name"}
    - output_key: str 结果保存到 state 的哪个 key

    权限说明：
    - 管理端：可以添加新工具，选择已有预设工具
    - 用户端：只能使用管理端已经添加好的工具节点，不能自主添加自定义代码
    """

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self._tool: Optional[Callable] = None
        self._init_tool()

    def _init_tool(self):
        """初始化工具，从配置加载"""
        tool_name = self.config.get(ToolNodeConfigFields.TOOL_NAME.value, self.id)
        log.info(f"初始化ToolNode: {tool_name}")

        # 如果是预注册的工具，直接获取
        if tool_name in _tool_registry:
            self._tool = _tool_registry[tool_name]
            log.info(f"ToolNode {tool_name}: 使用预注册工具")
        else:
            # 否则从配置中的 python_code 创建
            python_code = self.config.get(ToolNodeConfigFields.PYTHON_CODE.value)
            if python_code:
                try:
                    # 动态创建函数
                    namespace = {}
                    exec(python_code, namespace)
                    if 'tool_func' in namespace:
                        self._tool = namespace['tool_func']
                        log.info(f"ToolNode {tool_name}: 从python_code动态创建成功")
                    else:
                        log.error(f"ToolNode {tool_name}: python_code中必须定义tool_func函数")
                except Exception as e:
                    log.error(f"ToolNode {tool_name}: 解析python_code失败: {e}")

    @classmethod
    def register_tool(cls, name: str, func: Callable) -> None:
        """注册一个工具到全局注册表"""
        _tool_registry[name] = func
        log.info(f"注册工具成功: {name}")

    @classmethod
    def list_registered_tools(cls) -> Dict[str, Callable]:
        """列出所有已注册的工具"""
        return _tool_registry.copy()

    def _map_inputs(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """根据输入映射从state获取参数"""
        mapping = self.config.get(ToolNodeConfigFields.INPUT_MAPPING.value, {})
        params = {}

        # 如果没有配置映射，默认把整个state传进去
        if not mapping:
            return {"state": state}

        for param_name, state_key in mapping.items():
            # 支持变量引用: 从 variables 中获取，或者直接从state根获取
            if state_key in state.get("variables", {}):
                params[param_name] = state["variables"][state_key]
            elif state_key in state:
                params[param_name] = state[state_key]

        # 填充默认值
        for param_def in self.config.get(ToolNodeConfigFields.PARAMETERS.value, []):
            if param_def["name"] not in params and "default" in param_def:
                params[param_def["name"]] = param_def["default"]

        return params

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用（LangGraph会调用这个方法）"""
        tool_name = self.config.get(ToolNodeConfigFields.TOOL_NAME.value, self.id)
        output_key = self.config.get(ToolNodeConfigFields.OUTPUT_KEY.value, "tool_output")

        log.info(f"ToolNode {self.id}: 执行工具 {tool_name}")

        # 获取输入参数
        params = self._map_inputs(state)
        #params = {'query': '今天的美元对人民币汇率是多少', 'max_results': 5.0, 'topic': 'general'}

        # 执行工具
        try:
            if self._tool is not None:
                result = self._tool(**params)
                log.info(f"ToolNode {self.id}: 执行成功, result={str(result)[:200]}...")
            else:
                # 如果没有工具，直接返回参数处理结果（用于测试）
                result = {
                    "success": False,
                    "error": "No tool function found",
                    "params": params
                }
                log.warning(f"ToolNode {self.id}: 未找到工具函数")
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
            log.error(f"ToolNode {self.id}: 执行工具失败: {e}")

        # 添加success标记
        if isinstance(result, dict) and "success" not in result:
            result["success"] = True

        # 将工具结果保存到message
        content = json.dumps(result, ensure_ascii=False, indent=2)
        message = {
            "node_id": self.id,
            "node_type": self.type,
            "tool_name": tool_name,
            "params": params,
            "result": result,
            "content": content
        }

        # 返回更新到state
        # output_key 保存结果到state指定key，同时也保存到variables
        return {
            "messages": [message],
            output_key: result,
            "output": content,
            "variables": {
                output_key: result
            }
        }

    def stream(self, state: Dict[str, Any]) -> Iterator[tuple[str, str]]:
        """支持流式输出（如果工具是流式的）"""
        # 工具调用一般一次性完成，这里做兼容
        result = self.__call__(state)
        content = result["output"]
        yield content, content

    async def astream(self, state: Dict[str, Any]) -> "AsyncGenerator[tuple[Any, str], Any]":
        """异步流式输出兼容"""
        result = self.__call__(state)
        content = result["output"]
        yield content, content

# ============ Tavily 联网搜索 ============
from tavily import TavilyClient
if hasattr(settings, 'TAVILY_API_KEY') and settings.TAVILY_API_KEY:
    tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ):
        """Run a web search via Tavily"""
        log.info("调用搜索工具")
        return tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

    ToolNode.register_tool("internet_search", internet_search)
    log.info("Tavily internet_search 工具已注册")
else:
    log.info("TAVILY_API_KEY 未配置，internet_search 工具不可用")