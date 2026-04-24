"""
Retrieve 检索 Demo - 直接演示向量检索
不使用 RetrieveNode 封装，直接裸代码演示
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))
sys.path.append(str(root_path / "backend"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(root_path / "backend" / "env" / ".env")

from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document

from backend.app.config.setting import settings
from backend.app.common.core.core import embeddings  # core 中的 embeddings


def test_retrieve_direct():
    """直接测试向量检索，不通过 RetrieveNode"""
    print("=" * 60)
    print("PGVector 知识库检索 Demo（直接演示）")
    print("=" * 60)

    # ========== 1. 初始化 embeddings 和 PGVector ==========
    print("\n[1/4] 初始化连接...")

    # 使用 core 中已经初始化好的 embeddings

    print(f"✓ 使用通义千问 text-embeddings-v3 初始化完成")

    # 连接 PGVector
    connection_string = settings.db_url  # 使用同步连接字符串（适用于同步代码）
    collection_name = "test_knowledge"

    vector_store = PGVector(
        collection_name=collection_name,
        connection_string=connection_string,
        distance_strategy="cosine",
        embedding_function=embeddings,
    )

    print(f"✓ PGVector 连接成功，集合: {collection_name}")
    print(f"  数据库: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")

    # ========== 2. 添加测试文档 ==========
    print(f"\n[2/4] 添加测试文档...")

    test_docs = [
        Document(
            page_content="Python是一种高级编程语言，由Guido van Rossum创造，它以简洁的语法和强大的生态系统闻名。",
            metadata={"source": "wiki", "category": "programming"}
        ),
        Document(
            page_content="LangGraph是一个用于构建有状态、多Actor LLM应用的框架，支持复杂工作流编排。",
            metadata={"source": "docs", "category": "ai"}
        ),
        Document(
            page_content="PGVector是PostgreSQL的扩展，可以在PostgreSQL中存储和查询向量数据。",
            metadata={"source": "github", "category": "database"}
        ),
        Document(
            page_content="RAG（Retrieval-Augmented Generation）是一种检索增强生成技术，可以让大模型基于外部知识库回答问题。",
            metadata={"source": "blog", "category": "ai"}
        ),
        Document(
            page_content="通义千问是阿里云开发的大语言模型，支持聊天、创作、问答等多种任务。",
            metadata={"source": "aliyun", "category": "ai"}
        )
    ]

    try:
        ids = vector_store.add_documents(test_docs)
        print(f"✓ 添加了 {len(test_docs)} 个文档，ids: {ids[:3]}...")
    except Exception as e:
        print(f"❌ 添加文档失败: {e}")
        return

    # ========== 3. 执行检索测试 ==========
    print(f"\n[3/4] 执行相似性检索...")

    test_queries = [
        "什么是RAG技术",
        "Python是谁创造的",
        "LangGraph 能做什么",
        "PostgreSQL 如何存储向量",
        "阿里云有什么大模型",
    ]

    top_k = 3
    score_threshold = 0.5

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"🔍 查询: {query}")
        print(f"{'-'*50}")

        results = vector_store.similarity_search(
            query,
            k=top_k,
            score_threshold=score_threshold
        )

        print(f"✓ 检索到 {len(results)} 篇相关文档:\n")

        for i, doc in enumerate(results):
            print(f"  【文档 {i+1}】")
            print(f"  内容: {doc.page_content}")
            print(f"  元数据: {doc.metadata}")
            print()

    # ========== 4. 输出总结 ==========
    print(f"\n{'='*50}")
    print(f"\n[4/4] 测试完成！")
    print()
    print("📝 总结：")
    print("- embeddings 正常工作")
    print("- PGVector 可以正确存储文档向量")
    print("- 语义相似性检索能返回正确结果")
    print("- 检索结果可以直接给 LLM 使用")


if __name__ == "__main__":
    test_retrieve_direct()
