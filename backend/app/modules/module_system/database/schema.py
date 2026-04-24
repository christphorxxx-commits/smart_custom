"""
知识库API请求响应Schema
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from backend.app.common.core.base_schema import BaseSchema, UserBySchema


# ========== 知识库 ==========
class KnowledgeCreateSchema(BaseModel):
    """创建知识库请求（创建空知识库，后续增量添加文档）"""
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    embedding_model: str = Field(default="text-embedding-v4", description="Embedding模型")
    search_model: str = Field(default="qwen-max", description="搜索后回答LLM模型")
    text_process_model: Optional[str] = Field(default=None, description="文本预处理/问答提取模型")
    image_understand_model: Optional[str] = Field(default=None, description="图片理解模型")


class KnowledgeUpdateSchema(KnowledgeCreateSchema):
    """更新知识库请求"""
    id: int = Field(..., description="知识库ID")
    uuid: str = Field(..., description="知识库UUID")
    status: Optional[str] = Field(default=None, description="状态: idle/processing/completed/failed")
    document_count: Optional[int] = Field(default=None, description="当前文档数量")
    total_tokens: Optional[int] = Field(default=None, description="总token数")


class KnowledgeOutSchema(KnowledgeCreateSchema, BaseSchema, UserBySchema):
    """知识库详情响应"""

    collection_name: str = Field(..., description="向量表名称")
    dimension: int = Field(..., description="向量维度")
    is_deleted: bool = Field(..., description="是否软删除")

    model_config = {"from_attributes": True}


class KnowledgeListQuerySchema(BaseModel):
    """知识库列表查询"""
    page: int = Field(default=1, description="页码")
    page_size: int = Field(default=10, description="每页数量")
    status: Optional[str] = Field(default=None, description="按状态过滤")


class KnowledgeListResponse(BaseModel):
    """知识库列表响应"""
    total: int = Field(default=0, description="总数")
    data: List[dict] = Field(default_factory=list, description="列表数据")

    model_config = {"from_attributes": True}


# ========== 文档 ==========
class AddDocumentSchema(BaseModel):
    """添加文档到知识库请求
    说明：content 是单个切片内容，将存入 PGVector 向量库
    KnowledgeFile 只存文件元信息，不重复存储content
    """
    knowledge_uuid: str = Field(..., description="知识库UUID")
    title: str = Field(..., description="文件名/文档标题")
    content: str = Field(..., description="文档切片内容（已经切分好，将存入向量库）")
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    file_size: Optional[int] = Field(default=None, description="原始文件大小(字节)")
    chunk_count: Optional[int] = Field(default=1, description="切片总数")
    source: Optional[str] = Field(default=None, description="文档来源(文件路径/URL)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外元数据")


class AddDocumentResponse(BaseModel):
    """添加文档响应"""
    success: bool = Field(..., description="是否成功")
    document_id: Optional[int] = Field(None, description="文档ID")
    vector_id: Optional[str] = Field(None, description="向量ID")
    message: str = Field(default="", description="提示信息")


class DocumentDeleteSchema(BaseModel):
    """删除文档请求"""
    document_id: int = Field(..., description="文档ID")
    knowledge_uuid: str = Field(..., description="知识库UUID")


class KnowledgeFileInfoSchema(BaseModel):
    """文档信息响应"""
    id: int = Field(..., description="文档ID")
    uuid: str = Field(..., description="文档UUID")
    knowledge_base_id: int = Field(..., description="所属知识库ID")
    file_name: str = Field(..., description="文件名")
    description: Optional[str] = Field(default=None, description="文件描述")
    file_size: Optional[int] = Field(default=None, description="文件大小(字节)")
    chunk_count: int = Field(default=0, description="切片数量")
    source: Optional[str] = Field(default=None, description="来源")
    status: int = Field(default=0, description="状态: 0-处理中 1-成功 2-失败")
    is_deleted: bool = Field(..., description="是否软删除")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")
    created_id: Optional[int] = Field(default=None, description="创建人ID")
    updated_id: Optional[int] = Field(default=None, description="更新人ID")

    model_config = {"from_attributes": True}


# ========== 向量检索 ==========
class SearchQuerySchema(BaseModel):
    """知识库语义相似性检索请求"""
    knowledge_uuid: str = Field(..., description="知识库UUID")
    query: str = Field(..., description="查询文本")
    top_k: int = Field(default=5, description="返回结果数量")
    score_threshold: float = Field(default=0.5, description="相似度阈值")


class SearchResultItem(BaseModel):
    """单个检索结果"""
    document: str = Field(..., description="文档内容")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    score: float = Field(..., description="相似度分数")
    document_id: int = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")


class SearchResponse(BaseModel):
    """知识库检索响应"""
    success: bool = Field(..., description="是否成功")
    results: List[SearchResultItem] = Field(default_factory=list, description="检索结果列表")
    total: int = Field(default=0, description="结果数量")
