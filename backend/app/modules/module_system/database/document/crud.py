"""
文档CRUD操作
"""
from typing import List, Optional

from langchain_core.documents import Document

from backend.app.common.core.base_crud import CRUDBase
from backend.app.common.core.base_vector_crud import BaseVectorCRUD
from .model import KnowledgeFileModel
from .schema import DocumentCreateSchema, DocumentUpdateSchema
from ...auth.schema import AuthSchema


class KnowledgeFileCRUD(CRUDBase[KnowledgeFileModel, DocumentCreateSchema, DocumentUpdateSchema]):
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
            search={"knowledge_id": knowledge_base_id, "is_deleted": False},
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

    def list_chunks(
        self,
        page: int = 1,
        page_size: int = 10,
        file_id: Optional[int] = None
    ) -> dict:
        """
        分页获取知识库所有切片

        参数:
            page: 页码
            page_size: 每页数量
            file_id: 按文件ID过滤（可选）

        返回:
            dict: {total, items, page_no, page_size}
        """
        return self.vector_crud.get_all_documents(page, page_size, file_id)

    def search_chunks(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """
        按关键词搜索切片内容

        参数:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量

        返回:
            dict: {total, items, page_no, page_size}
        """
        return self.vector_crud.search_documents(keyword, page, page_size)
