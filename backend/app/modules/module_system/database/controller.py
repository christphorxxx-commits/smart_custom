"""
知识库API控制器
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.response import SuccessResponse, ErrorResponse
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from .schema import (
    KnowledgeCreateSchema,
    KnowledgeUpdateSchema,
    KnowledgeOutSchema,
    KnowledgeListQuerySchema,
    KnowledgeListResponse,
    AddDocumentSchema,
    DocumentDeleteSchema,
    SearchQuerySchema,
)
from .service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.post("/create", summary="创建知识库")
async def create_knowledge_base(
    data: KnowledgeCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    """创建空知识库，后续可增量添加文档"""
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.create_knowledge_base(auth, data)
    return SuccessResponse(msg="知识库创建成功",data=result)


@router.post("/update", summary="更新知识库信息")
async def update_knowledge_base(
    data: KnowledgeUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.update_knowledge_base(auth, data)
    if not result:
        return ErrorResponse(msg="知识库不存在")
    return SuccessResponse(data=result)


@router.get("/detail/{uuid}", summary="获取知识库详情")
async def get_knowledge_base_detail(
    uuid: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    kb = await KnowledgeBaseService.get_knowledge_base_by_uuid(auth, uuid)
    if not kb:
        return ErrorResponse(msg="知识库不存在")
    result = KnowledgeOutSchema.model_validate(kb)
    return SuccessResponse(data=result)


@router.post("/list", summary="获取当前用户的知识库列表")
async def list_knowledge_base(
    query: KnowledgeListQuerySchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.list_knowledge_base_by_user(
        auth,
        page=query.page,
        page_size=query.page_size,
        status=query.status
    )
    response = KnowledgeListResponse(
        total=result["total"],
        data=result["items"]
    )
    return SuccessResponse(data=response)


@router.delete("/delete/{kb_id}", summary="删除知识库")
async def delete_knowledge_base(
    kb_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    success = await KnowledgeBaseService.delete_knowledge_base(auth, kb_id)
    if not success:
        return ErrorResponse(msg="知识库不存在")
    return SuccessResponse(msg="删除成功")


@router.post("/document/add", summary="添加文档到知识库")
async def add_document(
    data: AddDocumentSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 先根据 knowledge_uuid 获取 kb
    kb = await KnowledgeBaseService.get_knowledge_base_by_uuid(auth, data.knowledge_uuid)
    if not kb:
        return ErrorResponse(msg="知识库不存在")

    result = await KnowledgeBaseService.add_document(auth, kb.id, data)
    if result.success:
        return SuccessResponse(data=result, msg=result.message)
    else:
        return ErrorResponse(msg=result.message)


@router.delete("/document/delete", summary="删除文档")
async def delete_document(
    data: DocumentDeleteSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 先根据 knowledge_uuid 获取 kb
    kb = await KnowledgeBaseService.get_knowledge_base_by_uuid(auth, data.knowledge_uuid)
    if not kb:
        return ErrorResponse(msg="知识库不存在")

    success = await KnowledgeBaseService.delete_document(auth, kb.id, data.document_id)
    if not success:
        return ErrorResponse(msg="文档不存在或删除失败")
    return SuccessResponse(msg="删除成功")


@router.post("/search", summary="语义相似性检索")
async def search_knowledge(
    query: SearchQuerySchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 先根据 knowledge_uuid 获取 kb
    kb = await KnowledgeBaseService.get_knowledge_base_by_uuid(auth, query.knowledge_uuid)
    if not kb:
        return ErrorResponse(msg="知识库不存在")

    result = await KnowledgeBaseService.search(
        knowledge_base_id=kb.id,
        query=query.query,
        top_k=query.top_k,
        score_threshold=query.score_threshold
    )
    if result.success:
        return SuccessResponse(data=result)
    return ErrorResponse(msg="检索失败")


@router.get("/document/list/{uuid}", summary="获取知识库的文件列表")
async def list_knowledge_files(
    uuid: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 先根据 uuid 获取 kb
    kb = await KnowledgeBaseService.get_knowledge_base_by_uuid(auth, uuid)
    if not kb:
        return ErrorResponse(msg="知识库不存在")
    # 获取文件列表
    files = await KnowledgeBaseService.list_files(auth, kb.id)
    return SuccessResponse(data=files)
