"""
向量库基础 CRUD
封装 PGVector 向量表操作，与业务层解耦
"""
from typing import List

from langchain_community.vectorstores import PGVector
from langchain_community.vectorstores.pgvector import DistanceStrategy
from langchain_core.documents import Document
from sqlalchemy import create_engine, text

from backend.app.config.setting import settings
from backend.app.common.core.core import embeddings
from backend.app.common.core.logger import log


class BaseVectorCRUD:
    """向量表基础操作类"""

    def __init__(self, collection_name: str):
        """
        初始化向量库 CRUD

        参数:
            collection_name: 向量表名称（知识库格式：kb_{id}_embedding）
        """
        self.collection_name = collection_name
        self.connection_string = settings.db_url
        self.vector_store = PGVector(
            collection_name=self.collection_name,
            connection_string=self.connection_string,
            distance_strategy=DistanceStrategy.COSINE,
            embedding_function=embeddings.embedding,
        )

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        添加文档到向量库

        参数:
            documents: LangChain Document 列表

        返回:
            List[str]: 插入后的向量 ID 列表
        """
        return self.vector_store.add_documents(documents)

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5
    ) -> List:
        """
        相似性检索（带相似度分数）

        参数:
            query: 查询文本
            k: 返回结果数量

        返回:
            List[(Document, float)]: (文档, 距离分数) 元组列表
        """
        return self.vector_store.similarity_search_with_score(query, k=k)

    def drop_collection(self) -> bool:
        """
        删除向量表（DROP TABLE）
        不依赖 PGVector 私有 API，直接用 SQLAlchemy 建连接

        返回:
            bool: 是否删除成功
        """
        try:
            engine = create_engine(self.connection_string)
            with engine.connect() as connection:
                connection.execute(text(f"DROP TABLE IF EXISTS {self.collection_name}"))
                connection.commit()
            return True
        except Exception as e:
            log.warning(f"删除向量表失败: {self.collection_name}, error={e}")
            return False
