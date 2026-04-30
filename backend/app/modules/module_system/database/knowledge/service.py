"""
知识库服务层
"""
from typing import List, Dict, Any, Optional

from fastapi import Path
from langchain_core.documents import Document
from pydantic import Field

from backend.app.common.core.exceptions import CustomException
from backend.app.common.core.logger import log
from backend.app.modules.module_system.auth.schema import AuthSchema
from .schema import (
    KnowledgeCreateSchema,
    KnowledgeOutSchema,
    KnowledgeUpdateSchema,
)
from .crud import KnowledgeCRUD
from .model import KnowledgeBaseModel
from backend.app.modules.module_system.database.document.crud import KnowledgeVectorCRUD, KnowledgeFileCRUD
from backend.app.modules.module_system.database.document.schema import DocumentOutSchema


class KnowledgeBaseService:
    """知识库服务"""

    @staticmethod
    async def get_knowledge(
        auth: AuthSchema,
        id: int,
    ) -> Dict[str, Any]:
        """根据UUID获取知识库"""
        obj = await KnowledgeCRUD(auth=auth).get([id])
        if not obj:
            raise CustomException(msg=f"知识库不存在，id:{id}")
        return KnowledgeOutSchema.model_validate(obj).model_dump()


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
    async def detail_service(cls, auth: AuthSchema, id: int) -> dict:
        obj = await KnowledgeCRUD(auth=auth).get(id=id)
        if not obj:
            raise CustomException(msg="应用不存在")
        return KnowledgeOutSchema.model_validate(obj).model_dump()

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
    def search_similar(
        cls,
        knowledge_base_id: int,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """语义相似性检索

        参数：
        - knowledge_id: 知识库ID
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
        # 校验知识库存在
        kb = await KnowledgeCRUD(auth=auth).get(id=kb_id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        kb_crud = KnowledgeFileCRUD(auth=auth)
        files = await kb_crud.list_by_knowledge_base_crud(kb_id)

        # 转换为字典，添加 knowledge_uuid，自动处理datetime序列化
        result = []
        for f in files:
            file_dict = DocumentOutSchema.model_validate(f).model_dump(mode='json')
            file_dict["knowledge_uuid"] = kb.uuid
            result.append(file_dict)
        return result

