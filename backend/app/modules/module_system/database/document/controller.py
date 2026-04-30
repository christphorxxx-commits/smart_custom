"""
文档API控制器
"""
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from backend.app.common.core.logger import log
from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.response import SuccessResponse
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from .schema import (
    DocumentCreateSchema,
    DocumentUpdateSchema,
    DocumentDeleteSchema,
)
from .service import DocumentService

DocumentRouter = APIRouter(prefix="/document", tags=["文档"])


@DocumentRouter.post("/add/{id}", summary="添加文档到知识库")
async def create_obj_controller(
    data: DocumentCreateSchema,
    id: int = Path(..., description="知识库id"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)

    result = await DocumentService.create_service(auth, id, data)
    log.info(f"添加文档成功: kb_id={id}, document_id={result.get('document_id')}")
    return SuccessResponse(data=result, msg="添加成功")


@DocumentRouter.post("/update", summary="更新文档元信息")
async def update_obj_controller(
    data: DocumentUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await DocumentService.update_service(auth=auth, doc_id=data.document_id, data=data)
    log.info(f"更新文档成功: document_id={data.document_id}")
    return SuccessResponse(data=result, msg="更新成功")


@DocumentRouter.delete("/delete", summary="删除文档")
async def delete_obj_controller(
    data: DocumentDeleteSchema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await DocumentService.delete_service(auth, data.knowledge_uuid, data.document_id)
    log.info(f"删除文档成功: document_id={data.document_id}")
    return SuccessResponse(data=result, msg="删除成功")


@DocumentRouter.get("/detail/{id}/{doc_id}", summary="获取文档详情")
async def get_obj_detail_controller(
    id: int = Path(..., description="文档ID"),
    doc_id: int = Path(..., description="文档ID"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 获取文档详情
    doc = await DocumentService.detail_service(auth, id, doc_id)
    log.info(f"获取文档详情成功: kb_id={id}, document_id={doc_id}")
    return SuccessResponse(data=doc, msg="获取成功")
