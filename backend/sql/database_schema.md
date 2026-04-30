# 知识库系统数据库表结构

本文档描述知识库模块的完整数据库表结构设计。

---

## 表结构总览

| 表名 | 类型 | 说明 |
|------|------|------|
| `knowledge_base` | 关系表 | 知识库主表 |
| `knowledge_file` | 关系表 | 文档元数据表（不存内容） |
| `kb_{id}_embedding` | 向量表 | 每个知识库对应1张向量表，存 content + 向量 |
| `langchain_pg_collection` | 向量系统表 | PGVector 集合管理表（LangChain 自动创建） |

> **设计原则**：content 只存在向量表中，关系表只存元数据和关联 ID，避免数据冗余。

---

## 1. knowledge_base（知识库主表）

所有 PostgreSQL 关系表都继承基类字段（`ModelMixin + UserMixin`）。

### 1.1 继承基类字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | Integer | PK, 自增 | 主键 ID |
| `uuid` | String(64) | NOT NULL, UNIQUE | 全局唯一标识 |
| `status` | String(10) | NOT NULL, DEFAULT '0' | 启用状态 (0:启用 1:禁用) |
| `description` | Text | NULLABLE | 备注/描述 |
| `created_time` | DateTime | NOT NULL | 创建时间 |
| `updated_time` | DateTime | NOT NULL | 更新时间 |
| `created_id` | Integer | FK, INDEX | 创建人 ID (关联 sys_user.id) |
| `updated_id` | Integer | FK, INDEX | 更新人 ID (关联 sys_user.id) |

### 1.2 业务字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `name` | String(256) | NOT NULL | 知识库名称 |
| `collection_name` | String(128) | NOT NULL, UNIQUE, INDEX | 关联的 PGVector 向量表名 |
| `embedding_model` | String(64) | DEFAULT 'text-embedding-v4' | 嵌入模型名称 |
| `search_model` | String(64) | DEFAULT 'qwen-max' | 问答模型名称 |
| `text_process_model` | String(64) | NULLABLE | 文本预处理模型 |
| `image_understand_model` | String(64) | NULLABLE | 图片理解模型 |
| `dimension` | Integer | DEFAULT 1536 | 向量维度 |
| `is_deleted` | Boolean | NOT NULL, DEFAULT FALSE | 是否软删除 |

### 1.3 关联关系

- **`files`**: 一对多关联 `KnowledgeFileModel`，通过 `knowledge_base.id = knowledge_file.knowledge_id` 逻辑关联
- **无物理外键约束**：使用 SQLAlchemy ORM 层面关联，数据库层面不建外键

---

## 2. knowledge_file（文档元数据表）

存储文档切片的元数据信息，**不存储实际内容**。实际内容存储在 PGVector 向量表中。

### 2.1 继承基类字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | Integer | PK, 自增 | 主键 ID |
| `uuid` | String(64) | NOT NULL, UNIQUE | 全局唯一标识 |
| `status` | String(10) | NOT NULL, DEFAULT '0' | 启用状态 |
| `description` | Text | NULLABLE | 备注/描述 |
| `created_time` | DateTime | NOT NULL | 创建时间 |
| `updated_time` | DateTime | NOT NULL | 更新时间 |
| `created_id` | Integer | FK, INDEX | 创建人 ID |
| `updated_id` | Integer | FK, INDEX | 更新人 ID |

### 2.2 业务字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `knowledge_id` | Integer | NOT NULL, INDEX | 所属知识库 ID |
| `title` | String(256) | NOT NULL | 文档标题/切片名称 |
| `file_name` | String(256) | NOT NULL | 原始文件名 |
| `file_size` | BigInteger | NULLABLE | 文件大小(字节) |
| `chunk_count` | Integer | DEFAULT 0 | 切片数量 |
| `source` | String(512) | NULLABLE | 来源路径/URL |
| `status` | Integer | DEFAULT 0 | 处理状态 (0-处理中，1-成功，2-失败) |
| `vector_id` | String(128) | NULLABLE | PGVector 向量表中的行 ID |
| `meta_data` | JSON | NULLABLE | 文档元数据 (JSON 格式) |
| `is_deleted` | Boolean | NOT NULL, DEFAULT FALSE | 是否软删除 |

### 2.3 关联关系

- **`kb`**: 多对一关联 `KnowledgeBaseModel`
- **索引**：`idx_knowledge_base_id` - 加速查询某个知识库下的所有文档

---

## 3. langchain_pg_collection（PGVector 集合管理表）

由 LangChain PGVector 自动创建和管理，用于存储所有向量集合的元数据。

### 3.1 字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `uuid` | UUID | PK | 集合唯一标识 |
| `name` | VARCHAR | NOT NULL, UNIQUE | 集合名称（格式：`kb_{知识库id}_embedding） |
| `cmetadata` | JSON | NULLABLE | 集合自定义元数据 |

### 3.2 说明

- 每个知识库对应一条记录，`name` 字段与 `knowledge_base.collection_name` 一一对应
- 该表由 LangChain 内部管理，业务代码不直接操作此表

---

## 4. kb_{id}_embedding（知识库向量表）

每个知识库对应 **1 张独立的向量表**，表名格式：`kb_{知识库ID}_embedding`。

由 LangChain PGVector 自动创建和管理。

### 4.1 标准字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 向量行唯一标识 |
| `collection_id` | UUID | FK | 关联 `langchain_pg_collection.uuid` |
| `embedding` | vector | NOT NULL | 向量数据（维度由 `knowledge_base.dimension` 决定） |
| `document` | TEXT | NOT NULL | 文档原文内容（`page_content`） |
| `cmetadata` | JSON | NULLABLE | 文档元数据 |

### 4.2 cmetadata（元数据 JSON 结构

`cmetadata` 字段存储的 JSON 包含以下业务字段：

| 键名 | 类型 | 说明 |
|------|------|------|
| `title` | String | 文档标题 |
| `file_name` | String | 原始文件名 |
| `source` | String | 来源路径 |
| `knowledge_id` | Integer | 所属知识库 ID |
| `file_id` | Integer | 关联 `knowledge_file.id` |
| `...` | Any | 其他自定义元数据字段 |

### 4.3 说明

- **向量索引**：PGVector 自动为 `embedding` 字段建立向量索引（HNSW / IVFFlat）
- **距离策略**：默认使用 COSINE 余弦相似度
- **数据隔离**：每个知识库独立建表，数据完全隔离，便于管理和删除

---

## 5. ER 关系示意

```
┌──────────────────────────────────────────────────────────────────────┐
│                     knowledge_base                              │
├──────────────────────────────────────────────────────────────────┤
│  PK  id                                                         │
│      uuid (unique)                                               │
│      name                                                        │
│      collection_name  ───────────────────────────────────────────┐   │
│      ...                                                      │   │
│      is_deleted                                               │   │
└──────────────────────────────────────────────────────────────┼───┘
                                                               │
                                                               │
┌──────────────────────────────────────────────────────────────┼───┐
│                    knowledge_file                                         │   │
├──────────────────────────────────────────────────────────────┤   │
│  PK  id                                                     │   │
│      uuid                                                   │   │
│  FK  knowledge_id  ────────────────────────────────────────┘   │
│      title                                                    │
│      file_name                                                │
│      vector_id  ───────────────────────────────────────────┐   │
│      ...                                                    │   │
│      is_deleted                                             │   │
└────────────────────────────────────────────────────────────┼───┘
                                                             │
                                                             │
┌────────────────────────────────────────────────────────────┼─────┐
│              kb_{id}_embedding                             │     │
├────────────────────────────────────────────────────────────┤     │
│  PK  id                                                     │     │
│  FK  collection_id  ───────────────────────────────────────┘     │
│      embedding                                                 │
│      document (content)                                         │
│      cmetadata {file_id, ...}                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 设计要点

1. **数据分层存储
   - 关系表存元数据，向量表存内容 + 向量
   - 通过 `vector_id` 和 `knowledge_id` 双向关联

2. **软删除机制**
   - 关系表使用 `is_deleted` 软删除
   - 向量表物理 `DROP TABLE` 彻底删除（删除知识库时）

3. **无物理外键
   - ORM 层面管理关联关系
   - 便于分库分表和数据迁移
   - 避免软删除时外键约束问题

4. **索引优化**
   - `knowledge_base.collection_name` 唯一索引
   - `knowledge_file.knowledge_id` 普通索引
   - 向量表自动建立向量索引
