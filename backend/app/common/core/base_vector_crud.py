"""
向量库基础 CRUD
封装 PGVector 向量表操作，与业务层解耦
参考 base_crud.py 的 Page 模式实现标准化分页查询

三表两库架构：
1. knowledge_base (关系型) - 知识库元信息，collection_name = kb_{id}
2. knowledge_file (关系型) - 文档文件元信息，通过 knowledge_id 关联
3. kb_{id} (PGVectorStore v2) - 切片向量存储，一个知识库一张表

PGVectorStore v2 表结构（kb_{id}）：
- langchain_id (str, 主键)
- content (str, 文本内容)
- embedding (vector, 向量)
- langchain_metadata (JSONB, 元数据: file_id, file_name, knowledge_id, chunk_index, total_chunks 等)
"""
from typing import List, Dict, Any, Optional, Type

from langchain_core.documents import Document
from langchain_postgres import PGVectorStore
from pydantic import BaseModel
from sqlalchemy import create_engine, text

from backend.app.config.setting import settings
from backend.app.common.core.core import embeddings
from backend.app.common.core.logger import log
from .database import async_engine, engine
from backend.app.modules.module_system.database.document.schema import ChunkOutSchema


class BaseVectorCRUD:
    """向量表基础操作类"""

    def __init__(self, table_name: str):
        """
        初始化向量库 CRUD

        参数:
            table_name: 向量表名称（知识库格式：kb_{id}）
        """
        self.table_name = table_name
        self.vector_store = PGVectorStore.create_sync(
            engine=async_engine,
            embedding_service=embeddings,
            table_name=self.table_name,
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
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List:
        """
        相似性检索（带相似度分数）

        参数:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件

        返回:
            List[(Document, float)]: (文档, 距离分数) 元组列表
        """
        return self.vector_store.similarity_search_with_score(query, k=k, filter=filter)

    def drop_collection(self) -> bool:
        """
        删除整个向量表（DROP TABLE）
        当知识库删除时调用，删除 kb_{id} 表

        返回:
            bool: 是否删除成功
        """
        try:
            with engine.connect() as connection:
                connection.execute(text(f"DROP TABLE IF EXISTS {self.table_name}"))
                connection.commit()
            log.info(f"删除向量表成功: {self.table_name}")
            return True
        except Exception as e:
            log.warning(f"删除向量表失败: {self.table_name}, error={e}")
            return False

    def get_all_documents(
        self,
        page: int = 1,
        page_size: int = 10,
        file_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        分页获取所有切片文档（兼容旧接口）
        """
        return self.page(
            page=page,
            page_size=page_size,
            file_id=file_id,
            out_schema=None
        )

    def page(
        self,
        page: int = 1,
        page_size: int = 20,
        file_id: Optional[int] = None,
        keyword: Optional[str] = None,
        out_schema: Optional[Type[BaseModel]] = ChunkOutSchema
    ) -> Dict[str, Any]:
        """
        标准化分页查询方法（参考 base_crud.py 的 Page 模式）

        PGVectorStore v2 表结构：
        - langchain_id: 主键
        - content: 文本内容
        - embedding: 向量
        - langchain_metadata: JSONB 元数据（包含 file_id, file_name, knowledge_id, chunk_index 等）

        参数:
            page: 页码，从1开始
            page_size: 每页数量
            file_id: 按文件ID过滤（可选）
            keyword: 搜索关键词（模糊匹配content字段，可选）
            out_schema: 输出数据模型，默认 ChunkOutSchema

        返回:
            Dict: {total, items, page_no, page_size}
        """
        try:
            offset = (page - 1) * page_size

            # 1. 构建查询条件
            where_conditions = ["1 = 1"]  # 避免空 WHERE 子句问题
            params = {}

            if file_id is not None:
                where_conditions.append("langchain_metadata->>'file_id' = :file_id")
                params["file_id"] = str(file_id)

            if keyword:
                where_conditions.append("content LIKE :keyword")
                params["keyword"] = f"%{keyword}%"

            where_clause = "WHERE " + " AND ".join(where_conditions)

            # 2. 查询总数
            count_sql = f"SELECT COUNT(*) FROM {self.table_name} {where_clause}"
            with engine.connect() as connection:
                result = connection.execute(text(count_sql), params)
                total = result.scalar() or 0

            # 3. 分页查询数据 - 按切片序号排序，保证同一文件的切片连续
            sql = f"""
                SELECT langchain_id, content, langchain_metadata
                FROM {self.table_name}
                {where_clause}
                ORDER BY (langchain_metadata->>'chunk_index')::int NULLS LAST, langchain_id
                LIMIT :limit OFFSET :offset
            """
            params["limit"] = page_size
            params["offset"] = offset

            with engine.connect() as connection:
                result = connection.execute(text(sql), params)
                rows = result.fetchall()

            # 4. 转换为字典列表，并解析 langchain_metadata 中的常用字段
            items = []
            for row in rows:
                item = {
                    "id": str(row[0]),  # langchain_id 转字符串
                    "document": row[1],  # content 映射到 document（保持 API 兼容）
                    "content": row[1],  # 原始字段名
                    "cmetadata": row[2],  # 旧字段名（保持兼容性）
                    "langchain_metadata": row[2],  # 原始字段名（PGVectorStore v2）
                }
                # 从 langchain_metadata 中解析常用字段
                metadata = row[2] or {}
                # 兼容 document_id（MetadataSchema 新命名）和 file_id（旧命名）
                item["file_id"] = metadata.get("document_id") or metadata.get("file_id")
                item["file_name"] = metadata.get("file_name") or metadata.get("title")
                item["knowledge_id"] = metadata.get("knowledge_id")
                item["chunk_index"] = metadata.get("chunk_index")
                item["total_chunks"] = metadata.get("total_chunks")
                items.append(item)

            # 5. 如果指定了 out_schema，则进行类型转换
            if out_schema:
                items = [out_schema.model_validate(item).model_dump() for item in items]

            return {
                "total": total,
                "items": items,
                "page_no": page,
                "page_size": page_size
            }
        except Exception as e:
            log.warning(f"分页查询失败: {self.table_name}, error={e}")
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
        page_size: int = 20,
        out_schema: Optional[Type[BaseModel]] = ChunkOutSchema
    ) -> Dict[str, Any]:
        """
        按关键词搜索切片内容（使用LIKE模糊查询）
        已合并到 page 方法，保留该方法用于向后兼容

        参数:
            keyword: 搜索关键词
            page: 页码，从1开始
            page_size: 每页数量
            out_schema: 输出数据模型，默认 ChunkOutSchema

        返回:
            Dict: {total, items, page_no, page_size}
        """
        return self.page(
            page=page,
            page_size=page_size,
            keyword=keyword,
            out_schema=out_schema
        )

    def delete_by_file_id(self, file_id: int) -> int:
        """
        删除指定文件的所有切片向量（删除单个文档，保留知识库）

        参数:
            file_id: 文件ID

        返回:
            int: 删除的记录数
        """

        try:
            with engine.connect() as connection:
                result = connection.execute(
                    text(f"DELETE FROM {self.table_name} WHERE langchain_metadata->>'file_id' = :file_id"),
                    {"file_id": str(file_id)}
                )
                connection.commit()
                deleted_count = result.rowcount
                log.info(f"删除文件切片向量成功: file_id={file_id}, count={deleted_count}")
                return deleted_count
        except Exception as e:
            log.warning(f"删除文件切片向量失败: {self.table_name}, file_id={file_id}, error={e}")
            return 0

    def delete_by_ids(self, ids: List[str]) -> int:
        """
        按ID批量删除切片向量

        参数:
            ids: 切片ID列表

        返回:
            int: 删除的记录数
        """
        if not ids:
            return 0
        try:
            with engine.connect() as connection:
                # 构建 IN 条件
                placeholders = ", ".join([f":id_{i}" for i in range(len(ids))])
                params = {f"id_{i}": str(id_val) for i, id_val in enumerate(ids)}

                result = connection.execute(
                    text(f"DELETE FROM {self.table_name} WHERE langchain_id IN ({placeholders})"),
                    params
                )
                connection.commit()
                deleted_count = result.rowcount
                log.info(f"批量删除切片向量成功: count={deleted_count}")
                return deleted_count
        except Exception as e:
            log.warning(f"批量删除切片向量失败: {self.table_name}, error={e}")
            return 0

    def get_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        按ID获取单个切片

        参数:
            chunk_id: 切片ID (langchain_id)

        返回:
            Optional[Dict]: 切片信息，不存在返回None
        """
        try:
            with engine.connect() as connection:
                result = connection.execute(
                    text(f"""
                        SELECT langchain_id, content, langchain_metadata
                        FROM {self.table_name}
                        WHERE langchain_id = :chunk_id
                    """),
                    {"chunk_id": chunk_id}
                )
                row = result.fetchone()
                if not row:
                    return None

                metadata = row[2] or {}
                return {
                    "id": str(row[0]),
                    "document": row[1],
                    "content": row[1],
                    "cmetadata": row[2],
                    "langchain_metadata": row[2],
                    "file_id": metadata.get("file_id"),
                    "file_name": metadata.get("file_name"),
                    "knowledge_id": metadata.get("knowledge_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "total_chunks": metadata.get("total_chunks"),
                }
        except Exception as e:
            log.warning(f"获取切片失败: {self.table_name}, id={chunk_id}, error={e}")
            return None

    def count(self, file_id: Optional[int] = None) -> int:
        """
        获取切片总数（支持按文件过滤）

        参数:
            file_id: 可选，按文件ID过滤

        返回:
            int: 切片总数
        """
        try:
            where_clause = ""
            params = {}
            if file_id is not None:
                where_clause = "WHERE langchain_metadata->>'file_id' = :file_id"
                params["file_id"] = str(file_id)

            with engine.connect() as connection:
                result = connection.execute(
                    text(f"SELECT COUNT(*) FROM {self.table_name} {where_clause}"),
                    params
                )
                return result.scalar() or 0
        except Exception as e:
            log.warning(f"统计切片数失败: {self.table_name}, error={e}")
            return 0

    def get_file_chunk_ids(self, file_id: int) -> List[str]:
        """
        获取指定文件的所有切片ID列表

        参数:
            file_id: 文件ID

        返回:
            List[str]: 切片ID列表
        """
        try:
            with engine.connect() as connection:
                result = connection.execute(
                    text(f"""
                        SELECT langchain_id
                        FROM {self.table_name}
                        WHERE langchain_metadata->>'file_id' = :file_id
                        ORDER BY (langchain_metadata->>'chunk_index')::int NULLS LAST
                    """),
                    {"file_id": str(file_id)}
                )
                rows = result.fetchall()
                return [str(row[0]) for row in rows]
        except Exception as e:
            log.warning(f"获取文件切片ID失败: {self.table_name}, file_id={file_id}, error={e}")
            return []
