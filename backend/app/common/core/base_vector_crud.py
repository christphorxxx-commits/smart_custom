"""
向量库基础 CRUD
封装 PGVector 向量表操作，与业务层解耦
"""
from typing import List, Dict, Any, Optional

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
            embedding_function=embeddings,
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

    def get_all_documents(
        self,
        page: int = 1,
        page_size: int = 10,
        file_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        分页获取所有切片文档

        参数:
            page: 页码，从1开始
            page_size: 每页数量
            file_id: 按文件ID过滤（可选）

        返回:
            Dict: {total, items, page_no, page_size}
        """
        try:
            engine = create_engine(self.connection_string)
            offset = (page - 1) * page_size

            # 构建查询条件
            where_clause = ""
            params = {}
            if file_id is not None:
                where_clause = "WHERE cmetadata->>'file_id' = :file_id"
                params["file_id"] = str(file_id)

            # 查询总数
            count_sql = f"SELECT COUNT(*) FROM {self.collection_name} {where_clause}"
            with engine.connect() as connection:
                result = connection.execute(text(count_sql), params)
                total = result.scalar() or 0

            # 分页查询数据
            sql = f"""
                SELECT id, document, cmetadata
                FROM {self.collection_name}
                {where_clause}
                ORDER BY id
                LIMIT :limit OFFSET :offset
            """
            params["limit"] = page_size
            params["offset"] = offset

            with engine.connect() as connection:
                result = connection.execute(text(sql), params)
                rows = result.fetchall()

            # 转换为字典列表
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": row[2]
                })

            return {
                "total": total,
                "items": items,
                "page_no": page,
                "page_size": page_size
            }
        except Exception as e:
            log.warning(f"获取切片列表失败: {self.collection_name}, error={e}")
            return {
                "total": 0,
                "items": [],
                "page_no": page,
                "page_size": page_size
            }

    def search_documents(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        按关键词搜索切片内容（使用LIKE模糊查询）

        参数:
            keyword: 搜索关键词
            page: 页码，从1开始
            page_size: 每页数量

        返回:
            Dict: {total, items, page_no, page_size}
        """
        try:
            engine = create_engine(self.connection_string)
            offset = (page - 1) * page_size
            search_pattern = f"%{keyword}%"

            # 查询总数
            count_sql = f"SELECT COUNT(*) FROM {self.collection_name} WHERE document LIKE :keyword"
            with engine.connect() as connection:
                result = connection.execute(text(count_sql), {"keyword": search_pattern})
                total = result.scalar() or 0

            # 分页查询数据
            sql = f"""
                SELECT id, document, cmetadata
                FROM {self.collection_name}
                WHERE document LIKE :keyword
                ORDER BY id
                LIMIT :limit OFFSET :offset
            """
            with engine.connect() as connection:
                result = connection.execute(text(sql), {
                    "keyword": search_pattern,
                    "limit": page_size,
                    "offset": offset
                })
                rows = result.fetchall()

            # 转换为字典列表
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": row[2]
                })

            return {
                "total": total,
                "items": items,
                "page_no": page,
                "page_size": page_size
            }
        except Exception as e:
            log.warning(f"搜索切片失败: {self.collection_name}, keyword={keyword}, error={e}")
            return {
                "total": 0,
                "items": [],
                "page_no": page,
                "page_size": page_size
            }
