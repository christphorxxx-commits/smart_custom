"""
知识库服务层
"""
from typing import List, Dict, Any, Optional

from langchain_community.vectorstores.pgvector import DistanceStrategy
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
from sqlalchemy import text

from backend.app.common.core.logger import log
from backend.app.config.setting import settings
from backend.app.common.core.core import embeddings
from backend.app.modules.module_system.auth.schema import AuthSchema
from .schema import (
    AddDocumentSchema,
    AddDocumentResponse,
    KnowledgeCreateSchema,
    KnowledgeOutSchema,
    KnowledgeUpdateSchema,
    SearchQuerySchema,
    SearchResponse,
    SearchResultItem,
)
from .crud import KnowledgeBaseCRUD, KnowledgeFileCRUD
from .model import KnowledgeBase, KnowledgeFile


class KnowledgeBaseService:
    """知识库服务"""

    @staticmethod
    async def create_knowledge_base(
        auth: AuthSchema,
        data: KnowledgeCreateSchema
    ) -> dict:
        """创建空知识库
        创建后自动生成 collection_name = kb_{id}_embedding
        """
        # CRUD 层处理创建和自动生成 collection_name
        kb_crud = KnowledgeBaseCRUD(auth=auth)
        kb = await kb_crud.create_with_collection_name(data)

        log.info(f"创建知识库成功: id={kb.id}, uuid={kb.uuid}, name={kb.name}, collection_name={kb.collection_name}")
        return KnowledgeOutSchema.model_validate(kb).model_dump()

    @staticmethod
    async def update_knowledge_base(
        auth: AuthSchema,
        data: KnowledgeUpdateSchema
    ) -> Dict[str, Any]:
        """更新知识库信息"""
        kb_crud = KnowledgeBaseCRUD(auth=auth)
        kb = await kb_crud.update(data.id, data)
        if not kb:
            log.error(f"知识库不存在：id={kb.id}, uuid={kb.uuid}")
            return {"success":"False","message":"知识库不存在"}
        log.info(f"更新知识库成功: id={kb.id}, uuid={kb.uuid}")
        return {
            "kb_id":kb.id,
            "message":"更新成功"
        }


    @staticmethod
    async def get_knowledge_base_by_uuid(
        auth: AuthSchema,
        uuid: str
    ) -> Optional[KnowledgeBase]:
        """根据UUID获取知识库"""
        kb_crud = KnowledgeBaseCRUD(auth=auth)
        return await kb_crud.get_by_uuid_crud(uuid)

    @staticmethod
    async def list_knowledge_base_by_user(
        auth: AuthSchema,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """分页列出用户的知识库"""
        kb_crud = KnowledgeBaseCRUD(auth=auth)
        search = {}
        if status:
            search["status"] = status
        if auth.user:
            search["created_id"] = auth.user.id

        result = await kb_crud.page(
            offset=(page - 1) * page_size,
            limit=page_size,
            order_by=[{"id": "desc"}],
            search=search,
            out_schema=KnowledgeOutSchema
        )
        return result

    @staticmethod
    async def delete_knowledge_base(
        auth: AuthSchema,
        kb_id: int
    ) -> bool:
        """删除知识库
        - 软删除关系表记录
        - DROP TABLE 向量表
        """
        kb_crud = KnowledgeBaseCRUD(auth=auth)
        kb = await kb_crud.get(id=kb_id)
        if not kb:
            return False

        # 1. 软删除关系表
        await kb_crud.delete([kb_id])

        # 2. 删除向量表
        collection_name = f"kb_{kb.id}_embedding"
        connection_string = settings.db_url

        try:
            vector_store = PGVector(
                collection_name=collection_name,
                connection_string=connection_string,
                distance_strategy="cosine",
                embedding_function=embeddings.embedding,
            )
            # DROP TABLE
            with vector_store._get_connection() as connection:
                connection.execute(text(f"DROP TABLE IF EXISTS {collection_name}"))
                connection.commit()
            log.info(f"删除知识库向量表成功: {collection_name}")
        except Exception as e:
            log.warning(f"删除向量表失败: {collection_name}, error={e}")

        log.info(f"删除知识库成功: id={kb_id}, name={kb.name}")
        return True

    @staticmethod
    async def add_document(
        auth: AuthSchema,
        kb_id: int,
        data: AddDocumentSchema
    ) -> AddDocumentResponse:
        """添加文档切片到知识库
        步骤：
        1. 保存文件元数据到关系表（不存content，只存元信息）
        2. 计算向量并将(content+向量)插入到 PGVector 向量表
        3. 更新知识库文档计数
        """
        kb_crud = KnowledgeBaseCRUD(auth=auth)
        file_crud = KnowledgeFileCRUD(auth=auth)
        try:
            # 1. 获取知识库
            kb = await kb_crud.get(id=kb_id)
            if not kb:
                return AddDocumentResponse(
                    success=False,
                    message="知识库不存在"
                )

            # 2. 保存文件元数据到 PostgreSQL 关系表（content不在这里存）
            doc_data = data.model_dump(exclude={"content", "metadata"})
            doc_data["knowledge_base_id"] = kb_id
            doc = await file_crud.create(doc_data)

            # 3. 添加到 PGVector 向量库（content+向量存在这里）
            connection_string = settings.db_url
            collection_name = f"kb_{kb.id}_embedding"

            vector_store = PGVector(
                collection_name=collection_name,
                connection_string=connection_string,
                distance_strategy=DistanceStrategy.COSINE,
                embedding_function=embeddings.embedding,
            )

            # 创建 Document 对象，content存在这里供检索使用
            document = Document(
                page_content=data.content,
                metadata={
                    "title": data.title,
                    "file_name": data.file_name or data.title,
                    "source": data.source,
                    "knowledge_base_id": kb_id,
                    "file_id": doc.id,
                    **(data.metadata or {})
                }
            )

            # 插入向量到 PGVector
            ids = vector_store.add_documents([document])

            log.info(f"添加文档成功: kb_id={kb_id}, title={data.file_name}, doc_id={doc.id}")

            return AddDocumentResponse(
                success=True,
                document_id=doc.id,
                vector_id=ids[0] if ids else None,
                message="添加成功"
            )

        except Exception as e:
            log.error(f"添加文档失败: {e}")
            return AddDocumentResponse(
                success=False,
                message=f"添加失败: {str(e)}"
            )

    @staticmethod
    async def delete_document(
        auth: AuthSchema,
        kb_id: int,
        doc_id: int
    ) -> bool:
        """删除文档
        - 软删除关系表
        - 删除向量表中的对应向量
        """
        kb_crud = KnowledgeBaseCRUD(auth=auth)
        file_crud = KnowledgeFileCRUD(auth=auth)
        try:
            # 1. 获取文档
            doc = await file_crud.get(id=doc_id)
            if not doc:
                return False

            kb = await kb_crud.get(id=kb_id)
            if not kb:
                return False

            # 2. 软删除文档
            await file_crud.delete([doc_id])

            # 3. 删除向量（LangChain PGVector 不支持单条删除，需要重建索引
            # 这里先标记删除，定期批量重建索引
            collection_name = f"kb_{kb_id}_embedding"
            log.info(f"文档已标记删除: {collection_name}, doc_id={doc_id}")

            log.info(f"删除文档成功: kb_id={kb_id}, doc_id={doc_id}")
            return True

        except Exception as e:
            log.error(f"删除文档失败: {e}")
            return False

    @staticmethod
    def search_similar(
        knowledge_base_id: int,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """语义相似性检索

        参数：
        - knowledge_base_id: 知识库ID
        - query: 查询文本
        - top_k: 返回结果数量
        - score_threshold: 相似度阈值
        """
        connection_string = settings.db_url
        collection_name = f"kb_{knowledge_base_id}_embedding"

        vector_store = PGVector(
            collection_name=collection_name,
            connection_string=connection_string,
            distance_strategy=DistanceStrategy.COSINE,
            # distance_strategy="cosine",
            embedding_function=embeddings.embedding,
        )

        # 执行相似性检索
        results = vector_store.similarity_search_with_score(
            query,
            k=top_k
        )

        # 格式化结果
        output = []
        for doc, score in results:
            output.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": 1.0 - score,  # distance → similarity （距离越小越相似）
                "document_id": doc.metadata.get("file_id"),
                "title": doc.metadata.get("title"),
            })

        return output

    @staticmethod
    async def search(
        knowledge_base_id: int,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> SearchResponse:
        """检索入口"""
        results = KnowledgeBaseService.search_similar(
            knowledge_base_id=knowledge_base_id,
            query=query,
            top_k=top_k,
            score_threshold=score_threshold
        )

        # 转换为响应格式
        result_items = []
        for item in results:
            result_items.append(SearchResultItem(
                document=item["content"],
                metadata=item["metadata"],
                score=item["score"],
                document_id=item["document_id"] if item["document_id"] else 0,
                title=item["title"] if item["title"] else ""
            ))

        return SearchResponse(
            success=True,
            results=result_items,
            total=len(result_items)
        )

    @staticmethod
    async def list_files(
        auth: AuthSchema,
        kb_id: int
    ) -> List[dict]:
        """列出知识库下所有文件"""
        from .schema import KnowledgeFileInfoSchema
        kb_crud = KnowledgeFileCRUD(auth=auth)
        files = await kb_crud.list_by_knowledge_base_crud(kb_id)
        # 转换为字典，自动处理datetime序列化
        return [KnowledgeFileInfoSchema.model_validate(f).model_dump(mode='json') for f in files]



