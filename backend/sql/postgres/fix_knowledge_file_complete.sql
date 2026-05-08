-- 完整修复 knowledge_file 表结构，匹配 SQLAlchemy Model
-- 问题：数据库 schema 与 Model 定义多处不一致
-- 执行时间：2026-05-08

-- =================================================================
-- 1. 添加缺失的字段
-- =================================================================

-- 添加 title 字段（文档标题/切片名称）
ALTER TABLE public.knowledge_file
ADD COLUMN IF NOT EXISTS title character varying(256) NOT NULL DEFAULT '';

-- 添加 vector_id 字段（PGVector向量表中的行ID）
ALTER TABLE public.knowledge_file
ADD COLUMN IF NOT EXISTS vector_id character varying(128);

-- 添加 meta_data 字段（文档元数据JSON格式）
ALTER TABLE public.knowledge_file
ADD COLUMN IF NOT EXISTS meta_data json;

-- =================================================================
-- 2. 重命名字段 knowledge_base_id -> knowledge_id
-- =================================================================

-- 先删除旧的索引
DROP INDEX IF EXISTS idx_knowledge_file_knowledge_base_id;

-- 重命名字段
ALTER TABLE public.knowledge_file
RENAME COLUMN knowledge_base_id TO knowledge_id;

-- 创建新的索引
CREATE INDEX IF NOT EXISTS idx_knowledge_id ON public.knowledge_file USING btree (knowledge_id);

-- =================================================================
-- 3. 添加字段注释
-- =================================================================

COMMENT ON COLUMN public.knowledge_file.knowledge_id IS '所属知识库ID';
COMMENT ON COLUMN public.knowledge_file.title IS '文档标题/切片名称';
COMMENT ON COLUMN public.knowledge_file.vector_id IS 'PGVector向量表中的行ID';
COMMENT ON COLUMN public.knowledge_file.meta_data IS '文档元数据(JSON格式)';

-- =================================================================
-- 4. 数据迁移：将 file_name 的值复制到 title 字段（如果 title 为空）
-- =================================================================

-- 把 file_name 的值同步到 title（向后兼容）
UPDATE public.knowledge_file
SET title = file_name
WHERE title = '' OR title IS NULL;

-- =================================================================
-- 5. 验证修改结果
-- =================================================================

-- 查看最终表结构（执行后取消注释）
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'knowledge_file'
-- ORDER BY ordinal_position;
