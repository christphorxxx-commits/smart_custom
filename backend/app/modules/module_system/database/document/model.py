"""
文档数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Index, Text, JSON
from sqlalchemy.orm import relationship

from backend.app.common.core.base_model import ModelMixin, UserMixin


class KnowledgeFileModel(ModelMixin, UserMixin):
    __tablename__ = "document"

    # 只存知识库ID，不做外键约束（因为是软删除，不物理删除）
    knowledge_id: Column = Column(Integer, nullable=False, comment="所属知识库ID")

    title: Column = Column(String(256), nullable=False, comment="文档标题/切片名称")
    file_name: Column = Column(String(256), nullable=False, comment="原始文件名")
    description: Column = Column(Text, nullable=True, comment="文件描述")
    file_size: Column = Column(BigInteger, nullable=True, comment="文件大小(字节)")
    chunk_count: Column = Column(Integer, default=0, comment="切片数量")
    source: Column = Column(String(512), nullable=True, comment="来源路径")
    status: Column = Column(Integer, default=0, comment="0-处理中，1-成功，2-失败")
    vector_id: Column = Column(String(128), nullable=True, comment="PGVector向量表中的行ID")
    meta_data: Column = Column(JSON, nullable=True, comment="文档元数据(JSON格式)")
    is_deleted: Column = Column(Boolean, default=False, nullable=False, comment="是否软删除")

    # 反向关联（逻辑关联，使用字符串延迟解析）
    kb = relationship(
        "KnowledgeBaseModel",
        primaryjoin="KnowledgeBaseModel.id == KnowledgeFileModel.knowledge_id",
        foreign_keys="KnowledgeFileModel.knowledge_id",
        back_populates="files"
    )

    # 性能优化：给 knowledge_id 加索引，查询某个知识库下的文件时会快很多
    __table_args__ = (
        Index('idx_knowledge_id', 'knowledge_id'),
    )
