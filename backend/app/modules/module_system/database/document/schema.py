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
    """更新文档请求 - 仅更新元信息，不修改向量内容"""
    document_id: int = Field(..., description="文档ID")
    title: Optional[str] = Field(default=None, description="文件名/文档标题")  # type: ignore[assignment]
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    file_size: Optional[int] = Field(default=None, description="原始文件大小(字节)")
    chunk_count: Optional[int] = Field(default=None, description="切片总数")
    source: Optional[str] = Field(default=None, description="文档来源(文件路径/URL)")
    description: Optional[str] = Field(default=None, description="文件描述")
    meta_data: Optional[Dict[str, Any]] = Field(default=None, description="额外元数据")
    knowledge_uuid: Optional[str] = Field(default=None, description="知识库UUID(可迁移知识库)")
    content: Optional[str] = Field(default=None, description="文档切片内容（更新元信息时不修改向量内容）")
    status: Optional[int] = Field(default=None, description="状态: 0-处理中 1-成功 2-失败")


class DocumentDeleteSchema(BaseModel):
    """删除文档请求"""
    document_id: int = Field(..., description="文档ID")
    knowledge_uuid: str = Field(..., description="知识库UUID")


class DocumentOutSchema(DocumentCreateSchema, BaseSchema, UserBySchema):
    """文档信息响应 - 统一输出格式"""
    knowledge_id: int = Field(..., description="所属知识库ID")
    vector_id: Optional[str] = Field(default=None, description="向量ID(PGVector)")
    is_deleted: bool = Field(..., description="是否软删除")


class DocumentActionResponse(BaseModel):
    """文档操作响应（创建/更新/删除通用）"""
    success: bool = Field(..., description="是否成功")
    document_id: Optional[int] = Field(None, description="文档ID")
    vector_id: Optional[str] = Field(None, description="向量ID")
    message: str = Field(default="", description="提示信息")


# ========== 兼容别名（逐步迁移） ==========
AddDocumentSchema = DocumentCreateSchema
AddDocumentResponse = DocumentActionResponse
KnowledgeFileInfoSchema = DocumentOutSchema
