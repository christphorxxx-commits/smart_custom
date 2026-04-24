"""
向量知识库数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Index, Text
from sqlalchemy.orm import relationship

from backend.app.common.core.base_model import ModelMixin, UserMixin


# ==========================================
# 表 1: 知识库主表
# ==========================================
class KnowledgeBase(ModelMixin, UserMixin):
    __tablename__ = "knowledge_base"

    # 基础信息
    name: Column = Column(String(256), nullable=False, comment="知识库名称")
    # collection_name 加上唯一索引，防止重复创建表
    collection_name: Column = Column(String(128), nullable=False, unique=True, index=True,
                                     comment="关联的PGVector向量表名")

    # 模型配置
    embedding_model: Column = Column(String(64), default="text-embedding-v4", comment="嵌入模型")
    search_model: Column = Column(String(64), default="qwen-max", comment="问答模型")
    text_process_model: Column = Column(String(64), nullable=True, comment="文本预处理模型")
    image_understand_model: Column = Column(String(64), nullable=True, comment="图片理解模型")
    dimension: Column = Column(Integer, default=1536, comment="向量维度")

    # 软删除
    is_deleted: Column = Column(Boolean, default=False, nullable=False, comment="是否软删除")

    # 关联文件表（逻辑关联，不做数据库外键约束）
    files = relationship(
        "KnowledgeFile",
        primaryjoin="KnowledgeBase.id == KnowledgeFile.knowledge_base_id",
        foreign_keys="KnowledgeFile.knowledge_base_id",
        back_populates="kb",
        # 注意：这里不能用 cascade="all, delete-orphan"，因为软删除不会物理删除行，
        # 否则会报错或导致逻辑混乱。你需要自己在代码里处理级联软删除。
    )


# ==========================================
# 表 2: 文档/文件元数据表
# ==========================================
# 设计思路：软删除 + 应用层维护关系，不做数据库外键约束
# ==========================================
class KnowledgeFile(ModelMixin, UserMixin):
    __tablename__ = "knowledge_file"

    # 只存知识库ID，不做外键约束（因为是软删除，不物理删除）
    knowledge_base_id: Column = Column(Integer, nullable=False, comment="所属知识库ID")

    file_name: Column = Column(String(256), nullable=False, comment="文件名")
    description: Column = Column(Text, nullable=True, comment="文件描述")
    file_size: Column = Column(BigInteger, nullable=True, comment="文件大小(字节)")
    chunk_count: Column = Column(Integer, default=0, comment="切片数量")
    source: Column = Column(String(512), nullable=True, comment="来源路径")
    status: Column = Column(Integer, default=0, comment="0-处理中，1-成功，2-失败")
    is_deleted: Column = Column(Boolean, default=False, nullable=False, comment="是否软删除")

    # 反向关联（逻辑关联）
    # 【修改点】反向关联也要指定条件
    kb = relationship(
        "KnowledgeBase",
        primaryjoin="KnowledgeBase.id == KnowledgeFile.knowledge_base_id",
        foreign_keys="KnowledgeFile.knowledge_base_id",
        back_populates="files"
    )

    # 性能优化：给 knowledge_base_id 加索引，查询某个知识库下的文件时会快很多
    __table_args__ = (
        Index('idx_knowledge_base_id', 'knowledge_base_id'),
    )