"""
知识库CRUD操作
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.app.common.core.base_crud import CRUDBase
from .model import KnowledgeBase, KnowledgeFile
from .schema import AddDocumentSchema, KnowledgeCreateSchema, KnowledgeUpdateSchema
from ..auth.schema import AuthSchema


class KnowledgeBaseCRUD(CRUDBase[KnowledgeBase, KnowledgeCreateSchema, KnowledgeUpdateSchema]):
    """知识库（集合）CRUD"""

    def __init__(self, auth: AuthSchema):
        self.auth = auth
        super().__init__(model=KnowledgeBase, auth=auth)

    async def get_by_uuid_crud(
        self,
        uuid: str
    ) -> Optional[KnowledgeBase]:
        """根据UUID获取知识库"""
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.uuid == uuid,
            KnowledgeBase.is_deleted.is_(False)
        )
        result = await self.auth.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_with_collection_name(
        self,
        data: KnowledgeCreateSchema
    ) -> Optional[KnowledgeBase]:
        """创建知识库并自动生成 collection_name

        因为 collection_name 需要使用自增 id，所以需要先插入再更新
        """
        # 先创建记录获取自增 id
        kb = await self.create(data)

        # 自动生成 collection_name = kb_{id}_embedding
        collection_name = f"kb_{kb.id}_embedding"
        stmt = update(KnowledgeBase).where(
            KnowledgeBase.id == kb.id
        ).values(
            collection_name=collection_name
        )
        await self.auth.db.execute(stmt)
        await self.auth.db.commit()

        # 重新获取更新后的数据
        return await self.get(id=kb.id)

    async def list_by_user_crud(
            self,
        user_id: int
    ) -> List[KnowledgeBase]:
        """列出用户创建的所有知识库"""
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.created_id == user_id,
            KnowledgeBase.is_deleted.is_(False)
        ).order_by(KnowledgeBase.created_time.desc())
        result = await self.auth.db.execute(stmt)
        await self.auth.db.commit()
        return list(result.scalars().all())


class KnowledgeFileCRUD(CRUDBase[KnowledgeFile, AddDocumentSchema, KnowledgeUpdateSchema]):
    """知识库文件（单个文档切片）CRUD"""

    def __init__(self, auth: AuthSchema):
        self.auth = auth
        super().__init__(model=KnowledgeFile, auth=auth)


    async def list_by_knowledge_base_crud(
            self,
        knowledge_base_id: int
    ) -> List[KnowledgeFile]:
        """列出知识库下所有文档"""
        stmt = select(KnowledgeFile).where(
            KnowledgeFile.knowledge_base_id == knowledge_base_id,
            KnowledgeFile.is_deleted.is_(False)
        ).order_by(KnowledgeFile.created_time.desc())
        result = await self.auth.db.execute(stmt)
        await self.auth.db.commit()
        return list(result.scalars().all())



