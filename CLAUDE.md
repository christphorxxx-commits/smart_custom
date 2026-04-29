# CLAUDE.md

本文档给 Claude Code 提供这个仓库的开发指导。

## 项目概述

基于 LangGraph 的全栈 AI 对话与工作流编排项目。

- **后端**: FastAPI + Uvicorn (Python)
- **前端**: 两个独立前端
  - `webui/` - **用户端**: 普通用户使用，AI对话、工作流对话
  - `frontend/` - **管理端**: 管理人员使用，工作流创建管理等
- **数据库**: PostgreSQL (用户数据 + PGVector 向量存储) + MongoDB (对话历史 + 工作流定义)
- **AI**: LangChain + LangGraph + 通义千问大模型/嵌入

## 整体架构

### 后端结构
```
backend/
├── app/
│   ├── common/
│   │   ├── core/            # 基础类 (BaseNode, BaseMongoDocument, 数据库连接, 依赖)
│   │   ├── config/         # 配置和环境变量
│   │   └── utils/          # 工具函数
│   └── modules/
│       ├── api/ai/         # 普通 AI 对话（带记忆功能）
│       ├── workflow/       # LangGraph 工作流系统
│       │   ├── app.py      # 工作流 App 类（编译+运行）
│       │   ├── controller.py  # API 接口
│       │   ├── crud.py      # MongoDB CRUD
│       │   ├── model.py    # 工作流 MongoDB 模型
│       │   ├── schema.py   # 基础 Schema (State, Node, Edge)
│       │   └── nodes/      # 节点类型
│       │               ├── LLMNode.py      - LLM 生成节点
│       │               ├── RouterNode.py  - 条件路由节点
│       │               └── RetrieveNode.py - PGVector 知识库检索节点
│       ├── asr/           # 自动语音识别
│       ├── tts/           # 文本转语音
│       └── module_system  # 用户认证系统 (JWT)
└── env/                  # .env 文件（不提交到git）

main.py                 # 后端入口
```

### 前端结构

**1. webui/ (用户端)**
```
webui/
├── src/
│   ├── pages/
│   │   ├── Home.vue            # 普通 AI 对话主页
│   │   ├── WorkflowEditor.vue  # 工作流可视化编辑器
│   │   ├── WorkflowChat.vue     # 运行工作流对话
│   │   ├── Login.vue
│   │   └── Register.vue
│   ├── router/
│   └── main.js
```

**2. frontend/ (管理端)**
```
frontend/
├── src/
│   ├── pages/
│   └── ...
```

### 主要功能
1. **LangGraph 工作流编排** - 可视化拖拽编辑，保存到 MongoDB，流式运行输出
2. **RAG 支持** - RetrieveNode 使用 PGVector + 通义千问嵌入做知识库检索
3. **SSE 流式输出** - 普通对话和工作流都支持 Token 级流式输出
4. **多模态** - 支持 ASR 语音识别和 TTS 语音合成
5. **用户认证** - 基于 JWT 的登录注册系统
6. **权限分离** - 管理端 (frontend) 负责工作流创建管理，用户端 (webui) 负责对话使用

## 常用命令

### 启动后端
```bash
# 项目根目录执行
python main.py
```
默认运行在 `http://localhost:8000` (端口在 `backend/app/config/setting.py` 配置)。

### 启动用户端前端 (webui)
```bash
cd webui
npm install    # 第一次运行需要安装依赖
npm run dev
```
默认运行在 `http://localhost:3000`。

### 启动管理端前端 (frontend)
```bash
cd frontend
npm install    # 第一次运行需要安装依赖
npm run dev
```

### 安装依赖
```bash
# 后端
pip install -r requirements.txt

# 用户端
cd webui && npm install

# 管理端
cd frontend && npm install
```

## 重要说明

- **端口配置**: 后端端口在 `settings.SERVER_PORT` 定义，两个前端的代理配置都需要对应修改：
  - `webui/vite.config.js`
  - `frontend/vite.config.js`
- **环境变量**: 需要在 `backend/env/.env` 配置：
  - `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` (PostgreSQL)
  - `DASHSCOPE_API_KEY` (阿里云通义千问 API 密钥)
  - `JWT_SECRET_KEY`
  - 可选 MongoDB 配置
- **MongoDB 基类**: 所有 MongoDB 文档继承 `backend/app/common/core/base_model.py` 中的 `BaseMongoDocument`，自动包含通用字段 (`is_deleted`, `created_at`, `updated_at` 等)。
- **SQLAlchemy 模型**: 所有 PostgreSQL 表模型继承 `backend/app/common/core/base_model.py` 中的 `Base`，自动包含通用字段 (`id`, `is_deleted`, `created_at`, `updated_at`)。
  ```python
  from sqlalchemy import Column, Integer, String, Text
  from sqlalchemy.dialects import postgresql
  from backend.app.common.core.base_model import Base

  class YourModel(Base):
      __tablename__ = "table_name"
      # your fields here...
  ```
- **新增工作流节点**: 添加新节点类型步骤：
  1. 在 `workflow/nodes/` 创建 `.py` 文件，继承 `BaseNode`
  2. 在 `workflow/app.py` 添加 import
  3. 在 `_build_node_instances` 和 `compile` 方法中添加 case
- **认证**: 所有工作流/对话接口都需要通过 `get_current_user` 依赖做 JWT 认证
- **接口请求**：所有接口都分层处理，controller层、service层、crud层，schema中定义接口输入输出数据格式
- **API 响应格式**: 统一使用 `SuccessResponse` 和 `ErrorResponse`，都继承自 `JSONResponse`:
  ```python
  # 成功响应
  return SuccessResponse(data=your_data, msg="success message")
  # 失败响应
  return ErrorResponse(msg="error message")
  ```

## 代码组织规范

### 后端API分层结构
所有HTTP接口都遵循**分层结构**，按模块组织在 `api/` 目录下：

```
backend/app/modules/{module_name}/api/
├── controller.py  # API 接口层：接收请求、参数校验、返回响应
├── service.py     # 业务逻辑层：处理业务流程，调用 CRUD
├── crud.py        # 数据访问层：封装数据库增删改查操作
├── model.py       # 数据模型：SQLAlchemy PG 模型 / Beanie MongoDB 模型
└── schema.py      # Pydantic：定义请求 (QuerySchema) 和响应 (InfoSchema) 数据结构
```

调用顺序：
```
controller ← 依赖注入获取 db/auth
    ↓
service (业务逻辑)
    ↓
crud (数据库操作)
```

### 代码风格规范（按 database 模块实践）

#### Service 层统一规范

| 特性 | 规范 | 示例 |
|------|------|------|
| **方法装饰器** | 统一用 `@classmethod` | `async def create_service(cls, auth, ...)` |
| **方法命名** | 动词 + `_service` 后缀 | `create_service`, `update_service`, `delete_service` |
| **返回类型** | 基础类型 `dict`，不用 Pydantic 包装 | `-> dict` / `-> Dict[str, Any]` |
| **数据转换** | 统一用 `Schema.model_validate(obj).model_dump()` | `KnowledgeOutSchema.model_validate(obj).model_dump()` |
| **错误处理** | 全部 `raise CustomException(msg="xxx")` | `raise CustomException(msg="更新失败，知识库不存在")` |
| **CRUD 调用** | 每次调用时实例化，传入 auth | `await KnowledgeCRUD(auth=auth).get(id=id)` |

**Service 层标准流程（create / update / detail / delete）：**
```python
@classmethod
async def xxx_service(cls, auth: AuthSchema, ...) -> Dict[str, Any]:
    """方法注释"""

    # 1. 前置校验（存在性、唯一性）
    obj = await KnowledgeCRUD(auth=auth).get(id=id)
    if not obj:
        raise CustomException(msg="xxx不存在")

    # 2. 额外业务校验（如重名、权限等）
    if xxx:
        raise CustomException(msg="xxx失败，xxx")

    # 3. 执行 CRUD 操作
    result = await KnowledgeCRUD(auth=auth).xxx(...)

    # 4. 返回基础类型 dict
    return xxx.model_dump()
```

---

#### Controller 层统一规范

```python
@router.post("/xxx", summary="接口描述")
async def xxx_controller(
    data: Schema,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(db_getter)
) -> JSONResponse:
    auth = AuthSchema(user=current_user, db=db)
    result = await KnowledgeBaseService.xxx_service(auth, ...)
    log.info(f"xxx成功: {xxx}")
    return SuccessResponse(data=result, msg="xxx成功")
```

| 特性 | 规范 |
|------|------|
| **方法命名** | 动词 + `_controller` 后缀 |
| **日志位置** | Controller 层打 info 日志，Service 层只打 warning/error |
| **不做业务判断** | 所有异常由 `CustomException` 全局处理器捕获 |
| **返回格式** | 统一 `SuccessResponse(data=result, msg="xxx")` |

---

#### 命名约定

| 层级 | 命名规则 | 示例 |
|------|---------|------|
| CRUD 类 | `{ModuleName}CRUD` | `KnowledgeCRUD`, `KnowledgeFileCRUD`, `KnowledgeVectorCRUD` |
| Service 方法 | `xxx_service` | `create_service`, `update_service` |
| Controller 方法 | `xxx_obj_controller` | `create_obj_controller`, `update_obj_controller` |

---

#### 分层依赖原则

```
controller → service → crud → base_crud / base_vector_crud
```

- **不跨层调用**：Controller 不直接调 CRUD
- **不泄露底层**：Service 不出现 PGVector、SQLAlchemy 等底层 API
- **统一入口**：所有数据库操作通过 CRUD 类，复用 base 层能力
