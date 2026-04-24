-- ============================================
-- PGVector 需要先安装扩展
-- 安装方法：
--  1. 源码安装: https://github.com/pgvector/pgvector
--  2. Docker: 使用 pgvector/pgvector 镜像
-- ============================================

-- 1. 创建 vector 扩展（需要超级用户权限）
CREATE EXTENSION IF NOT EXISTS vector;

-- 查看扩展版本
SELECT * FROM pg_extension WHERE extname = 'vector';

-- ============================================
-- 2. 创建向量表示例
-- ============================================

-- 创建知识库表
CREATE TABLE IF NOT EXISTS smart (
    id bigserial PRIMARY KEY,
    collection_id uuid,
    embedding vector(1024),  -- 向量维度，通义千问 text-embeddings-v3 是 1024 维
    document text,
    metadata jsonb
);

-- 创建索引（余弦相似度）
CREATE INDEX IF NOT EXISTS smart_embedding_idx
ON smart
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================
-- 3. 说明
-- ============================================
-- LangChain PGVector 会自动使用这个表
-- collection_id 用于区分不同的知识库集合
-- 检索示例：
-- SELECT document, embeddings <-> '[0.1, 0.2, ...]'::vector AS distance
-- FROM smart
-- ORDER BY distance
-- LIMIT 5;
-- ============================================

-- 查看表是否创建成功
SELECT table_name FROM information_schema.tables WHERE table_name = 'smart';
