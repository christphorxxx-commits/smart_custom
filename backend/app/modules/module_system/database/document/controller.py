"""
文档API控制器
"""
from fastapi import APIRouter, Depends, Path, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from backend.app.common.core.exceptions import CustomException
from backend.app.common.core.logger import log
from backend.app.common.core.dependencies import get_current_user, db_getter
from backend.app.common.response import SuccessResponse, ErrorResponse
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.model import UserModel
from .schema import (
    DocumentCreateSchema,
    DocumentUpdateSchema,
    DocumentDeleteSchema,
)
from .service import DocumentService

DocumentRouter = APIRouter(prefix="/document", tags=["文档"])


@DocumentRouter.post("/add/{knowledge_uuid}", summary="添加文档到知识库")
async def create_obj_controller(
    data: DocumentCreateSchema,
    knowledge_uuid: str = Path(..., description="知识库UUID"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)

    # 校验路径参数与请求体参数一致
    if data.knowledge_uuid != knowledge_uuid:
        raise CustomException(msg="路径参数 knowledge_uuid 与请求体参数不一致")

    result = await DocumentService.create_service(auth, knowledge_uuid, data)
    log.info(f"添加文档成功: knowledge_uuid={knowledge_uuid}, document_id={result.get('document_id')}")
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


@DocumentRouter.get("/detail/{knowledge_uuid}/{doc_id}", summary="获取文档详情")
async def get_obj_detail_controller(
    knowledge_uuid: str = Path(..., description="知识库UUID"),
    doc_id: int = Path(..., description="文档ID"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    # 获取文档详情
    doc = await DocumentService.detail_service(auth, knowledge_uuid, doc_id)
    log.info(f"获取文档详情成功: knowledge_uuid={knowledge_uuid}, document_id={doc_id}")
    return SuccessResponse(data=doc, msg="获取成功")


@DocumentRouter.post("/upload/{knowledge_uuid}", summary="上传文件到知识库（自动切片）")
async def upload_file_controller(
    knowledge_uuid: str = Path(..., description="知识库UUID"),
    file: UploadFile = File(..., description="上传的文件"),
    chunk_size: int = Form(500, description="切片大小"),
    chunk_overlap: int = Form(50, description="切片重叠"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)

    # 读取文件内容
    file_content = await file.read()
    file_name = file.filename or "unknown.txt"

    # 校验文件大小
    if len(file_content) == 0:
        raise CustomException(msg="文件内容为空")
    if len(file_content) > 50 * 1024 * 1024:  # 50MB
        raise CustomException(msg="文件大小不能超过 50MB")

    # 调用服务处理
    result = await DocumentService.upload_file_service(
        auth=auth,
        knowledge_uuid=knowledge_uuid,
        file_content=file_content,
        file_name=file_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    log.info(f"文件上传成功: knowledge_uuid={knowledge_uuid}, file_name={file_name}, chunks={result.get('chunk_count', 0)}")
    return SuccessResponse(data=result, msg="上传成功")
