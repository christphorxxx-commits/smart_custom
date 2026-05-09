"""
文档API请求响应Schema
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.app.common.core.base_schema import BaseSchema, UserBySchema


class DocumentCreateSchema(BaseModel):
    """创建文档请求 - 将文档切片存入 PGVector 向量库
    说明：content 是单个切片内容，将存入 PGVector 向量库
          KnowledgeFileModel 只存文件元信息，不重复存储 content
    """
    title: str = Field(..., description="文件名/文档标题")
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    file_size: Optional[int] = Field(default=None, description="原始文件大小(字节)")
    chunk_count: Optional[int] = Field(default=1, description="切片总数")
    source: Optional[str] = Field(default=None, description="文档来源(文件路径/URL)")
    description: Optional[str] = Field(default=None, description="文件描述")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="额外元数据")
    knowledge_uuid: str = Field(..., description="知识库UUID")
    content: str = Field(..., description="文档切片内容（已经切分好，将存入向量库）")
    model_config = {"from_attributes": True}


class DocumentUpdateSchema(DocumentCreateSchema):
    """更新文档请求 - 仅更新元信息，不修改向量内容
    所有字段可选，支持部分更新
    注意：content 字段继承自 CreateSchema 但不会被使用，因为向量内容不可修改
    """
    document_id: int = Field(..., description="文档ID")
    # 重写所有继承字段为 Optional，支持部分更新
    knowledge_uuid: Optional[str] = Field(default=None, description="目标知识库UUID（迁移知识库）")
    title: Optional[str] = Field(default=None, description="文档标题/切片名称")
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    file_size: Optional[int] = Field(default=None, description="原始文件大小(字节)")
    chunk_count: Optional[int] = Field(default=None, description="切片总数")
    source: Optional[str] = Field(default=None, description="文档来源(文件路径/URL)")
    description: Optional[str] = Field(default=None, description="文件描述")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="额外元数据")
    content: Optional[str] = Field(default=None, description="（仅继承，不使用）文档切片内容不可修改")  # type: ignore[assignment]
    status: Optional[int] = Field(default=None, description="状态: 0-处理中 1-成功 2-失败")


class DocumentDeleteSchema(BaseModel):
    """删除文档请求"""
    document_id: int = Field(..., description="文档ID")
    knowledge_uuid: str = Field(..., description="知识库UUID")


class DocumentOutSchema(DocumentCreateSchema, BaseSchema, UserBySchema):
    """文档信息响应 - 统一输出格式
    注意：content 字段继承自 CreateSchema，但关系表中不存储实际内容，
          仅在需要时从向量库查询切片内容
    """
    content: Optional[str] = Field(default=None, description="（仅继承，不存关系表）文档切片内容")  # type: ignore[assignment]
    knowledge_id: int = Field(..., description="所属知识库ID")
    knowledge_uuid: str = Field(..., description="所属知识库UUID")
    status: Optional[int] = Field(default=0, description="状态: 0-处理中 1-成功 2-失败")
    vector_id: Optional[str] = Field(default=None, description="向量ID(PGVector)")
    is_deleted: bool = Field(..., description="是否软删除")


class DocumentActionResponse(BaseModel):
    """文档操作响应（创建/更新/删除通用）"""
    success: bool = Field(..., description="是否成功")
    document_id: Optional[int] = Field(None, description="文档ID")
    vector_id: Optional[str] = Field(None, description="向量ID")
    message: str = Field(default="", description="提示信息")


class ChunkOutSchema(BaseModel):
    """切片信息响应 - 标准化向量表输出格式

    三表两库架构：
    - knowledge (关系型): 知识库元信息
    - document (关系型): 文档文件元信息
    - kb_{id} (PGVectorStore v2): 切片向量存储表

    kb_{id} 表字段映射：
    - id → langchain_id（向量ID）
    - document → content（切片文本内容）
    - langchain_metadata → 原始元数据JSON
    - file_id, file_name 等 → 从 langchain_metadata 解析的常用字段
    """
    id: str = Field(..., description="向量ID（PGVectorStore langchain_id）")
    document: str = Field(..., description="切片文本内容")
    file_id: Optional[int] = Field(default=None, description="所属文件ID（从langchain_metadata解析）")
    file_name: Optional[str] = Field(default=None, description="所属文件名（从langchain_metadata解析）")
    knowledge_id: Optional[int] = Field(default=None, description="所属知识库ID（从langchain_metadata解析）")
    chunk_index: Optional[int] = Field(default=None, description="切片序号（从langchain_metadata解析）")
    total_chunks: Optional[int] = Field(default=None, description="文件总切片数（从langchain_metadata解析）")
    langchain_metadata: Optional[Dict[str, Any]] = Field(default=None, description="原始元数据JSON（PGVectorStore v2）")
    model_config = {"from_attributes": True}


class ChunkListQuerySchema(BaseModel):
    """切片列表查询参数"""
    knowledge_uuid: str = Field(..., description="知识库UUID")
    file_id: Optional[int] = Field(default=None, description="按文件ID过滤")
    keyword: Optional[str] = Field(default=None, description="搜索关键词（模糊匹配内容）")
    page: int = Field(default=1, description="页码")
    page_size: int = Field(default=20, description="每页数量")

class MetadataSchema(BaseModel):
    """元数据参数"""
    knowledge_id: int = Field(..., description="知识库ID")
    document_id: int = Field(..., description="文档ID")
    file_name: str = Field(...,description="文档初始名")
    page: int = Field(..., description="切片在文档中的页码")
    chunk_index: int = Field(..., description="切片的序号")



