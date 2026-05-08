"""
文档服务层
"""
from typing import List, Dict, Any, Optional
import os
import tempfile

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.common.core.exceptions import CustomException
from backend.app.common.core.logger import log
from backend.app.modules.module_system.auth.schema import AuthSchema
from .schema import (
    DocumentCreateSchema,
    DocumentOutSchema,
    DocumentUpdateSchema,
)
from .crud import KnowledgeFileCRUD, KnowledgeVectorCRUD
from .model import KnowledgeFileModel
from backend.app.modules.module_system.database.knowledge.crud import KnowledgeCRUD


class DocumentService:
    """文档服务"""

    @classmethod
    async def create_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        data: DocumentCreateSchema
    ) -> Dict[str, Any]:
        """添加文档切片到知识库
        步骤：
        1. 保存文件元数据到关系表（不存content，只存元信息）
        2. 计算向量并将(content+向量)插入到 PGVector 向量表
        3. 更新知识库文档计数
        """
        kb_crud = KnowledgeCRUD(auth=auth)
        file_crud = KnowledgeFileCRUD(auth=auth)

        # 1. 获取知识库
        kb = await kb_crud.get(id=kb_id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        # 2. 保存文件元数据到 PostgreSQL 关系表（content不在这里存）
        doc_data = data.model_dump(exclude={"content", "knowledge_uuid"})
        doc_data["knowledge_id"] = kb_id
        doc = await file_crud.create(doc_data)

        # 3. 添加到 PGVector 向量库（content+向量存在这里）
        vector_crud = KnowledgeVectorCRUD(kb_id=kb.id)

        # 创建 Document 对象，content存在这里供检索使用
        document = Document(
            page_content=data.content,
            metadata={
                "title": data.title,
                "file_name": data.file_name or data.title,
                "source": data.source,
                "knowledge_id": kb_id,
                "file_id": doc.id,
                **(data.meta_data or {})
            }
        )

        # 插入向量到 PGVector
        ids = vector_crud.add_documents([document])

        # 4. 更新文档记录，保存 vector_id
        vector_id = ids[0] if ids else None
        if vector_id:
            await file_crud.update(doc.id, {"vector_id": vector_id})

        return {
            "document_id": doc.id,
            "vector_id": vector_id
        }

    @classmethod
    async def delete_service(
        cls,
        auth: AuthSchema,
        knowledge_uuid: str,
        doc_id: int
    ) -> Dict[str, Any]:
        """删除文档
        - 软删除关系表
        - 删除向量表中的对应向量
        """
        kb_crud = KnowledgeCRUD(auth=auth)
        file_crud = KnowledgeFileCRUD(auth=auth)

        # 1. 校验知识库存在
        kb = await kb_crud.get(uuid=knowledge_uuid)
        if not kb:
            raise CustomException(msg="知识库不存在")

        # 2. 校验文档存在
        doc = await file_crud.get(id=doc_id)
        if not doc:
            raise CustomException(msg="文档不存在")

        # 3. 软删除文档
        await file_crud.delete([doc_id])

        return {
            "deleted_id": doc_id,
            "kb_id": kb.id
        }

    @classmethod
    async def update_service(
        cls,
        auth: AuthSchema,
        doc_id: int,
        data: DocumentUpdateSchema
    ) -> Dict[str, Any]:
        """更新文档元信息
        - 仅更新元信息，不修改向量内容
        - 支持迁移知识库（修改 knowledge_id）
        """
        # 1. 校验当前知识库存在
        kb = await KnowledgeCRUD(auth=auth).get(uuid=data.knowledge_uuid)
        if not kb:
            raise CustomException(msg="知识库不存在")

        # 2. 校验文档存在
        doc = await KnowledgeFileCRUD(auth=auth).get(id=doc_id)
        if not doc:
            raise CustomException(msg="文档不存在")

        # 3. 如果指定了新的 knowledge_uuid，需要迁移知识库
        # 使用 exclude_unset=True 支持部分更新，只更新用户显式设置的字段
        update_data = data.model_dump(exclude={"document_id", "knowledge_uuid"}, exclude_unset=True)

        if data.knowledge_uuid and data.knowledge_uuid != kb.uuid:
            # 获取目标知识库
            target_kb = await KnowledgeCRUD(auth=auth).get(uuid=data.knowledge_uuid)
            if not target_kb:
                raise CustomException(msg="目标知识库不存在")
            update_data["knowledge_id"] = target_kb.id

        # 4. 更新文档
        updated_doc = await KnowledgeFileCRUD(auth=auth).update(doc_id, update_data)

        return DocumentOutSchema.model_validate(updated_doc).model_dump(mode='json')


    @classmethod
    async def detail_service(
        cls,
        auth: AuthSchema,
        id: int,
        doc_id: int
    ) -> Dict[str, Any]:
        """获取文档详情"""
        # 校验知识库存在
        kb = await KnowledgeCRUD(auth=auth).get(id=id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        doc = await KnowledgeFileCRUD(auth=auth).get(id=doc_id)
        if not doc:
            raise CustomException(msg="文档不存在")

        return DocumentOutSchema.model_validate(doc).model_dump(mode='json')

    @classmethod
    async def upload_file_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        file_content: bytes,
        file_name: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """
        上传文件并自动切片存入知识库

        参数:
            kb_id: 知识库ID
            file_content: 文件内容字节
            file_name: 文件名
            chunk_size: 切片大小
            chunk_overlap: 切片重叠

        返回:
            上传结果
        """
        kb_crud = KnowledgeCRUD(auth=auth)
        file_crud = KnowledgeFileCRUD(auth=auth)

        # 1. 获取知识库
        kb = await kb_crud.get(id=kb_id)
        if not kb:
            raise CustomException(msg="知识库不存在")

        # 2. 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            # 3. 加载文件内容
            content = DocumentService.load_file_content(tmp_path, file_name)
            if not content or len(content.strip()) == 0:
                raise CustomException(msg="文件内容为空")

            # 4. 文本切片
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
                length_function=len
            )
            chunks = text_splitter.split_text(content)

            if not chunks:
                raise CustomException(msg="切片后没有生成有效切片")

            # 5. 保存文件元数据（主文件记录）
            file_size = len(file_content)
            doc_data = {
                "title": file_name,
                "file_name": file_name,
                "file_size": file_size,
                "chunk_count": len(chunks),
                "source": file_name,
                "status": 1,  # 成功
                "knowledge_id": kb_id,
            }
            doc = await file_crud.create(doc_data)

            # 6. 创建 Document 对象列表
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "title": file_name,
                        "file_name": file_name,
                        "source": file_name,
                        "knowledge_id": kb_id,
                        "file_id": doc.id,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                ))

            # 7. 批量插入向量到 PGVector
            vector_crud = KnowledgeVectorCRUD(kb_id=kb.id)
            vector_ids = vector_crud.add_documents(documents)

            # 8. 更新文件记录，保存第一个 vector_id
            if vector_ids:
                await file_crud.update(doc.id, {"vector_id": vector_ids[0]})

            log.info(f"文件上传成功: {file_name}, 切片数: {len(chunks)}, 向量数: {len(vector_ids)}")

            return {
                "document_id": doc.id,
                "file_name": file_name,
                "file_size": file_size,
                "chunk_count": len(chunks),
                "vector_count": len(vector_ids)
            }

        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass

    @staticmethod
    def load_file_content(file_path: str, file_name: str) -> str:
        """根据文件扩展名加载文件内容"""
        ext = os.path.splitext(file_name)[1].lower()

        if ext in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.xml', '.html', '.css', '.java', '.go',
                   '.cpp', '.c', '.h', '.rs']:
            return DocumentService.load_text_file(file_path)
        elif ext == '.pdf':
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except ImportError:
                raise CustomException(msg="PDF 支持需要安装 PyPDF2：pip install PyPDF2")
        elif ext in ['.docx', '.doc']:
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(file_path)
                text = ""
                for para in doc.paragraphs:
                    text += para.text + "\n"
                return text
            except ImportError:
                raise CustomException(msg="Word 文档支持需要安装 python-docx：pip install python-docx")
        else:
            # 默认按文本加载
            return DocumentService.load_text_file(file_path)

    @staticmethod
    # 文档加载器
    def load_text_file(file_path: str) -> str:
        """加载纯文本文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise CustomException(msg="文件编码不支持，仅支持 UTF-8、GBK、GB2312 编码")



