from typing import Dict, Any, List

from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from pydantic import Field

from backend.app.common.core.base_node import BaseNode
from backend.app.config.setting import settings


from typing import Optional

class RetrieveNode(BaseNode):
    """知识库检索节点

    使用PGVector向量数据库，通义千问嵌入模型，根据当前state中的query/input检索相关知识库文档
    将检索结果写入state中，供后续节点使用
    """
    collection_name: str = Field(default="knowledge_base")
    top_k: int = Field(default=5)
    score_threshold: float = Field(default=0.5)
    output_field: str = Field(default="context")


    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        # 从配置覆盖默认值
        if "collection_name" in data.get("config", {}):
            collection_name = data["config"]["collection_name"]
            data["collection_name"] = collection_name
        if "top_k" in data.get("config", {}):
            top_k = data["config"]["top_k"]
            data["top_k"] = top_k
        if "score_threshold" in data.get("config", {}):
            score_threshold = data["config"]["score_threshold"]
            data["score_threshold"] = score_threshold
        if "output_field" in data.get("config", {}):
            output_field = data["config"]["output_field"]
            data["output_field"] = output_field

        super().__init__(**data)

        # 初始化通义千问嵌入模型
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key=settings.DASHSCOPE_API_KEY,
        )

        # 初始化PGVector连接
        # 从settings获取数据库连接信息，使用已有的postgresql配置
        connection_string = settings.async_db_url
        self.vector_store = PGVector(
            collection_name=self.collection_name,
            connection_string=connection_string,
            distance_strategy="cosine",
        )

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph调用该方法执行检索

        从state中获取查询文本，检索知识库，将结果写入state
        """
        # 获取查询文本：优先使用config指定的字段，否则使用input
        query_field = self.config.get("query_field", "input")
        query_text = state.get(query_field, state.get("input", ""))

        if not query_text:
            return {
                self.output_field: [],
                "retrieve_count": 0
            }

        # 执行相似性检索
        results: List[Document] = self.vector_store.similarity_search(
            query_text,
            k=self.top_k,
            score_threshold=self.score_threshold
        )

        # 提取检索结果内容
        retrieved_docs = [doc.page_content for doc in results]
        retrieved_metadata = [doc.metadata for doc in results]

        # 将检索结果拼接成上下文文本，也保留原始列表
        context_text = "\n\n---\n\n".join([
            f"【文档{i+1}】\n{doc}" for i, doc in enumerate(retrieved_docs)
        ])

        # 返回结果更新state
        return {
            # 拼接好的上下文文本，供LLM直接使用
            self.output_field: context_text,
            # 原始文档列表
            f"{self.output_field}_docs": retrieved_docs,
            # 原始元数据
            f"{self.output_field}_metadata": retrieved_metadata,
            # 检索到的文档数量
            "retrieve_count": len(retrieved_docs)
        }
