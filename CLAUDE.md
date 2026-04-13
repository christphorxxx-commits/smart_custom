# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack AI conversation & workflow orchestration project based on LangGraph.

- **Backend**: FastAPI + Uvicorn (Python)
- **Frontend**: Vue 3 + Vite (JavaScript)
- **Database**: PostgreSQL (users + PGVector) + MongoDB (chat history + workflow definitions)
- **AI**: LangChain + LangGraph + DashScope Tongyi LLM/Embedding

## Key Architecture

### Backend Structure
```
backend/
├── app/
│   ├── common/
│   │   ├── core/            # Base classes (BaseNode, BaseMongoDocument, db, dependencies)
│   │   ├── config/         # Settings & environment config
│   │   └── modules/
│   ├── modules/
│   │   ├── api/ai/         # Regular AI chat (with memory)
│   │   ├── workflow/       # LangGraph workflow system
│   │   │   ├── app.py      # Workflow App class (compiles & runs)
│   │   │   ├── controller.py  # API endpoints
│   │   │   ├── crud.py      # MongoDB CRUD
│   │   │   ├── model.py    # Workflow App MongoDB model
│   │   │   ├── schema.py   # Base schema (State, Node, Edge)
│   │   │   └── nodes/      # Node types
│   │   │               ├── LLMNode.py
│   │   │               ├── RouterNode.py
│   │   │               └── RetrieveNode.py  # PGVector knowledge base retrieval
│   │   ├── asr/           # Automatic speech recognition
│   │   ├── tts/           # Text to speech
│   │   └── module_system  # User auth system (JWT)
└── env/                  # .env file (not committed)

main.py                 # Backend entry point
```

### Frontend Structure
```
webui/
├── src/
│   ├── pages/
│   │   ├── Home.vue            # Regular AI chat home
│   │   ├── WorkflowEditor.vue  # Workflow diagram editor
│   │   ├── WorkflowChat.vue     # Run workflow chat
│   │   ├── Login.vue
│   │   └── Register.vue
│   ├── router/
│   └── main.js
```

### Key Features
1. **LangGraph Workflow Orchestration** - Visual drag-drop workflow editor, save to MongoDB, run with streaming
2. **RAG Support** - RetrieveNode uses PGVector + DashScope Embedding for knowledge base retrieval
3. **SSE Streaming** - Token-level streaming output for both regular chat and workflow
4. **Multi-modal** - ASR + TTS support
5. **User Authentication** - JWT-based login/register

## Common Commands

### Start Backend
```bash
# From project root
python main.py
```
Runs on `http://localhost:8000` by default (port configured in `backend/app/config/setting.py`).

### Start Frontend Dev Server
```bash
cd webui
npm install    # first time only
npm run dev
```
Runs on `http://localhost:3000`.

### Install Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd webui && npm install
```

## Important Notes

- **Port configuration**: Backend port defined in `settings.SERVER_PORT`, frontend proxy in `webui/vite.config.js` must match.
- **Environment variables**: Must have `.env` file in `backend/env/` with:
  - `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` (PostgreSQL)
  - `DASHSCOPE_API_KEY` (Alibaba Cloud DashScope for LLM/Embedding)
  - `JWT_SECRET_KEY`
  - Optional MongoDB config
- **MongoDB base model**: All MongoDB documents inherit from `BaseMongoDocument` in `backend/app/common/core/base_model.py` which provides common fields (is_deleted, created_at, updated_at, etc).
- **Workflow nodes**: Add new node types by:
  1. Create `.py` file in `workflow/nodes/` inheriting `BaseNode`
  2. Add `import` in `workflow/app.py`
  3. Add case in `_build_node_instances` and `compile` method
- **Authentication**: All workflow/chat endpoints require JWT auth via `get_current_user` dependency
