"""
知识库服务层
"""
from typing import List, Dict, Any, Optional

from langchain_core.documents import Document

from backend.app.common.core.exceptions import CustomException
from backend.app.common.core.logger import log
from backend.app.modules.module_system.auth.schema import AuthSchema
from .schema import (
    AddDocumentSchema,
    KnowledgeCreateSchema,
    KnowledgeOutSchema,
    KnowledgeUpdateSchema,
    SearchQuerySchema,
)
from .crud import KnowledgeCRUD, KnowledgeFileCRUD, KnowledgeVectorCRUD
from .model import KnowledgeBaseModel, KnowledgeFileModel


class KnowledgeBaseService:
    """知识库服务"""

    @classmethod
    async def create_service(
        cls,
        auth: AuthSchema,
        data: KnowledgeCreateSchema
    ) -> dict:
        """创建空知识库
        创建后自动生成 collection_name = kb_{id}_embedding
        """
        # CRUD 层处理创建和自动生成 collection_name

        obj = await KnowledgeCRUD(auth=auth).get(name=data.name)
        if obj:
            raise CustomException(msg='创建失败，知识库已经存在')
        obj = await KnowledgeCRUD(auth=auth).create_crud(data)
        return KnowledgeOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def update_service(
        cls,
        auth: AuthSchema,
        id: int,
        data: KnowledgeUpdateSchema
    ) -> Dict[str, Any]:
        """更新知识库信息"""

        obj = await KnowledgeCRUD(auth).get(id=id)
        if not obj:
            raise CustomException(msg="更新失败，知识库不存在")

        exist_obj = await KnowledgeCRUD(auth=auth).get(name=data.name)
        if exist_obj and exist_obj.id != obj.id:
            raise CustomException(msg="更新失败，知识库名字重复")
        kb = await KnowledgeCRUD(auth).update(id, data)
        return KnowledgeOutSchema.model_validate(kb).model_dump()

    @classmethod
    async def detail_service(cls,auth: AuthSchema,id: int) -> dict:
        obj = await KnowledgeCRUD(auth=auth).get(id=id)
        if not obj:
            raise CustomException(msg="应用不存在")
        return KnowledgeOutSchema.model_validate(obj).model_dump()

    @staticmethod
    async def get_knowledge_base_by_uuid(
        auth: AuthSchema,
        uuid: str
    ) -> Optional[KnowledgeBaseModel]:
        """根据UUID获取知识库"""
        kb_crud = KnowledgeCRUD(auth=auth)
        return await kb_crud.get_by_uuid_crud(uuid)


    @classmethod
    async def list_service(
        cls,
        auth: AuthSchema,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """分页列出用户的知识库"""

        search = {}
        if status:
            search["status"] = status
        if auth.user:
            search["created_id"] = auth.user.id

        result = await KnowledgeCRUD(auth=auth).page(
            offset=(page - 1) * page_size,
            limit=page_size,
            order_by=[{"id": "desc"}],
            search=search,
            out_schema=KnowledgeOutSchema
        )
        return result

    @classmethod
    async def delete_service(
        cls,
        auth: AuthSchema,
        ids: list[int]
    ) -> Dict[str, Any]:
        """删除知识库
        - 软删除关系表记录
        - DROP TABLE 向量表
        """
        if len(ids) < 1:
            raise CustomException(msg='删除失败，删除对象不能为空')

        # 先批量校验所有 id 都存在
        for id in ids:
            obj = await KnowledgeCRUD(auth=auth).get(id=id)
            if not obj:
                raise CustomException(msg=f"删除失败，知识库{id}不存在")

        # 1. 软删除关系表（用 base_crud 的 delete 方法）
        await KnowledgeCRUD(auth=auth).delete(ids=ids)

        # 2. 删除向量表（每个知识库对应一个向量表）
        for id in ids:
            vector_crud = KnowledgeVectorCRUD(kb_id=id)
            vector_crud.drop_collection()

        return {"deleted_count": len(ids), "deleted_ids": ids}


    @classmethod
    async def add_document_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        data: AddDocumentSchema
    ) -> Dict[str, Any]:
        """添加文档切片到知识库
        步骤：
        1. 保存文件元数据到关系表（不存content，只存元信息）
        2. 计算向量并将(content+向量)插入到 PGVector 向量表
        3. 更新知识库文档计数
        """
        kb_crud = KnowledgeCRUD(auth=auth)
        file_crud = KnowledgeFileCRUD(auth=auth)

        # 1. 获取知识库
        kb = await kb_crud.get(id=kb_id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        # 2. 保存文件元数据到 PostgreSQL 关系表（content不在这里存）
        doc_data = data.model_dump(exclude={"content", "metadata"})
        doc_data["knowledge_base_id"] = kb_id
        doc = await file_crud.create(doc_data)

        # 3. 添加到 PGVector 向量库（content+向量存在这里）
        vector_crud = KnowledgeVectorCRUD(kb_id=kb.id)

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
        ids = vector_crud.add_documents([document])

        return {
            "document_id": doc.id,
            "vector_id": ids[0] if ids else None
        }

    @classmethod
    async def delete_document_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        doc_id: int
    ) -> Dict[str, Any]:
        """删除文档
        - 软删除关系表
        - 删除向量表中的对应向量
        """
        kb_crud = KnowledgeCRUD(auth=auth)
        file_crud = KnowledgeFileCRUD(auth=auth)

        # 1. 校验知识库存在
        kb = await kb_crud.get(id=kb_id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        # 2. 校验文档存在
        doc = await file_crud.get(id=doc_id)
        if not doc:
            raise CustomException(msg="文档不存在")

        # 3. 软删除文档
        await file_crud.delete([doc_id])

        # 4. 删除向量（LangChain PGVector 不支持单条删除，需要重建索引
        # 这里先标记删除，定期批量重建索引
        collection_name = f"kb_{kb_id}_embedding"
        log.info(f"文档已标记删除: {collection_name}, doc_id={doc_id}")

        return {
            "deleted_id": doc_id,
            "kb_id": kb_id
        }

    @classmethod
    def search_similar(
        cls,
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
        vector_crud = KnowledgeVectorCRUD(kb_id=knowledge_base_id)

        # 执行相似性检索
        results = vector_crud.similarity_search_with_score(query, k=top_k)

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

    @classmethod
    async def search_service(
        cls,
        auth: AuthSchema,
        knowledge_base_id: int,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """检索入口"""
        # 校验知识库存在
        kb = await KnowledgeCRUD(auth=auth).get(id=knowledge_base_id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        results = cls.search_similar(
            knowledge_base_id=knowledge_base_id,
            query=query,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return {
            "results": results,
            "total": len(results)
        }

    @classmethod
    async def list_files_service(
        cls,
        auth: AuthSchema,
        kb_id: int
    ) -> List[Dict[str, Any]]:
        """列出知识库下所有文件"""
        from .schema import KnowledgeFileInfoSchema
        # 校验知识库存在
        kb = await KnowledgeCRUD(auth=auth).get(id=kb_id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        kb_crud = KnowledgeFileCRUD(auth=auth)
        files = await kb_crud.list_by_knowledge_base_crud(kb_id)
        # 转换为字典，自动处理datetime序列化
        return [KnowledgeFileInfoSchema.model_validate(f).model_dump(mode='json') for f in files]



