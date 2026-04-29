"""
知识库CRUD操作
"""
from typing import List, Optional

from langchain_core.documents import Document

from backend.app.common.core.base_crud import CRUDBase
from backend.app.common.core.base_vector_crud import BaseVectorCRUD
from .model import KnowledgeBaseModel, KnowledgeFileModel
from .schema import AddDocumentSchema, KnowledgeCreateSchema, KnowledgeUpdateSchema
from ..auth.schema import AuthSchema


class KnowledgeCRUD(CRUDBase[KnowledgeBaseModel, KnowledgeCreateSchema, KnowledgeUpdateSchema]):
    """知识库（集合）CRUD"""

    def __init__(self, auth: AuthSchema):
        self.auth = auth
        super().__init__(model=KnowledgeBaseModel, auth=auth)

    async def get_by_uuid_crud(
        self,
        uuid: str
    ) -> Optional[KnowledgeBaseModel]:
        """根据UUID获取知识库"""
        return await self.get(uuid=uuid, is_deleted=False)

    async def create_crud(
        self,
        data: KnowledgeCreateSchema
    ) -> Optional[KnowledgeBaseModel]:
        """创建知识库并自动生成 collection_name

        因为 collection_name 需要使用自增 id，所以需要先插入再更新
        """
        # 先创建记录获取自增 id
        kb = await self.create(data)

        # 自动生成 collection_name = kb_{id}_embedding
        collection_name = f"kb_{kb.id}_embedding"
        await self.update(id=kb.id, data={"collection_name": collection_name})

        # 重新获取更新后的数据
        return await self.get(id=kb.id)

    async def list_by_user_crud(
        self,
        user_id: int
    ) -> List[KnowledgeBaseModel]:
        """列出用户创建的所有知识库"""
        return await self.list(
            search={"created_id": user_id, "is_deleted": False},
            order_by=[{"created_time": "desc"}]
        )

    async def delete_crud(self, ids: list[int]) -> None:
        """
        批量删除应用

        参数:
        - ids (list[int]): 应用ID列表
        """
        return await self.delete(ids=ids)


class KnowledgeFileCRUD(CRUDBase[KnowledgeFileModel, AddDocumentSchema, KnowledgeUpdateSchema]):
    """知识库文件（单个文档切片）CRUD"""

    def __init__(self, auth: AuthSchema):
        self.auth = auth
        super().__init__(model=KnowledgeFileModel, auth=auth)


    async def list_by_knowledge_base_crud(
        self,
        knowledge_base_id: int
    ) -> List[KnowledgeFileModel]:
        """列出知识库下所有文档"""
        return await self.list(
            search={"knowledge_base_id": knowledge_base_id, "is_deleted": False},
            order_by=[{"created_time": "desc"}]
        )


class KnowledgeVectorCRUD:
    """知识库向量表 CRUD（封装 BaseVectorCRUD）"""

    def __init__(self, kb_id: int):
        """
        初始化知识库向量 CRUD

        参数:
            kb_id: 知识库 ID
        """
        self.kb_id = kb_id
        self.collection_name = f"kb_{kb_id}_embedding"
        self.vector_crud = BaseVectorCRUD(collection_name=self.collection_name)

    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量库"""
        return self.vector_crud.add_documents(documents)

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5
    ) -> List:
        """相似性检索"""
        return self.vector_crud.similarity_search_with_score(query, k=k)

    def drop_collection(self) -> bool:
        """删除向量表"""
        return self.vector_crud.drop_collection()



