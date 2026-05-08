"""
知识库API控制器
"""
from fastapi import APIRouter, Depends, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from backend.app.common.core.exceptions import CustomException
from backend.app.common.core.logger import log
from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.response import SuccessResponse
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from .schema import (
    KnowledgeCreateSchema,
    KnowledgeUpdateSchema,
    KnowledgeListQuerySchema,
    SearchQuerySchema,
)
from backend.app.modules.module_system.database.document.schema import ChunkListQuerySchema
from .service import KnowledgeBaseService

KnowledgeRouter = APIRouter(prefix="/knowledge", tags=["知识库"])


@KnowledgeRouter.post("/create", summary="创建知识库")
async def create_obj_controller(
    data: KnowledgeCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    """创建空知识库，后续可增量添加文档"""
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.create_service(auth, data)
    log.info(f"创建知识库成功: id={result['id']}, uuid={result['uuid']}, name={result['name']}, collection_name={result['collection_name']}")
    return SuccessResponse(msg="知识库创建成功", data=result)


@KnowledgeRouter.post("/update/{id}", summary="更新知识库信息")
async def update_obj_controller(
    data: KnowledgeUpdateSchema,
    id: int = Path(..., description="知识库id"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.update_service(auth=auth, id=id, data=data)
    log.info(f"更新知识库成功: id={result['id']}, uuid={result['uuid']}")
    return SuccessResponse(data=result, msg="更新知识库成功")


@KnowledgeRouter.get("/detail/{id}", summary="获取知识库详情")
async def get_obj_detail_controller(
    id: int = Path(..., description="知识库id"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result_dict = await KnowledgeBaseService.detail_service(auth, id)
    log.info(f"获取知识库详情成功{id}")
    return SuccessResponse(data=result_dict, msg="获取知识库详情成功成功")


@KnowledgeRouter.post("/list", summary="获取当前用户的知识库列表")
async def list_obj_controller(
    query: KnowledgeListQuerySchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.list_service(
        auth,
        page=query.page,
        page_size=query.page_size,
        status=query.status
    )
    log.info(f"获取知识库列表成功: total={result['total']}, page_no={result['page_no']}")
    return SuccessResponse(data=result, msg="查询知识库列表成功")


@KnowledgeRouter.post("/delete/batch", summary="批量删除知识库")
async def delete_obj_controller(
    ids: list[int] = Body(..., description="ID列表"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.delete_service(auth, ids)
    log.info(f"删除知识库成功: {ids}")
    return SuccessResponse(data=result, msg="删除成功")


@KnowledgeRouter.post("/search", summary="语义相似性检索")
async def search_controller(
    query: SearchQuerySchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 先根据 knowledge_uuid 获取 kb
    kb = await KnowledgeBaseService.get_knowledge_base_by_uuid(auth, query.knowledge_uuid)
    if not kb:
        raise CustomException(msg="知识库不存在")

    result = await KnowledgeBaseService.search_service(
        auth=auth,
        knowledge_base_id=kb.id,
        query=query.query,
        top_k=query.top_k,
        score_threshold=query.score_threshold
    )
    log.info(f"检索知识库成功: kb_id={kb.id}, hits={result['total']}")
    return SuccessResponse(data=result, msg="检索成功")


@KnowledgeRouter.get("/document/list/{uuid}", summary="获取知识库的文件列表")
async def list_files_controller(
    uuid: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 先根据 uuid 获取 kb
    kb = await KnowledgeBaseService.get_knowledge_base_by_uuid(auth, uuid)
    if not kb:
        raise CustomException(msg="知识库不存在")

    # 获取文件列表
    files = await KnowledgeBaseService.list_files_service(auth, kb.id)
    log.info(f"获取文件列表成功: kb_id={kb.id}, count={len(files)}")
    return SuccessResponse(data=files, msg="获取成功")


@KnowledgeRouter.post("/chunks/list", summary="获取知识库的切片列表（分页+搜索+过滤）")
async def list_chunks_controller(
    query: ChunkListQuerySchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.list_chunks_service(
        auth=auth,
        knowledge_uuid=query.knowledge_uuid,
        file_id=query.file_id,
        keyword=query.keyword,
        page=query.page,
        page_size=query.page_size
    )
    log.info(f"获取切片列表成功: kb_uuid={query.knowledge_uuid}, total={result['total']}, page_no={result['page_no']}")
    return SuccessResponse(data=result, msg="获取成功")
