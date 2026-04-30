"""
知识库API请求响应Schema
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from backend.app.common.core.base_schema import BaseSchema, UserBySchema


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
