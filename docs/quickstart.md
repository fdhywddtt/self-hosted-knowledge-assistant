# 快速开始

## 方式一：Docker Compose（推荐）

前置条件：Docker 与 Docker Compose。

```bash
cp .env.example .env
docker compose up --build
```

- 前端：http://localhost:8080
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

首次启动会自动执行数据库迁移。

## 方式二：本地开发

前置条件：Python 3.11+、Node 20+、PostgreSQL（带 pgvector）、Redis。

Windows PowerShell：

```powershell
.\scripts\dev.ps1
```

或手动执行：

```bash
python -m venv .venv
pip install -e "backend[dev]"
cd backend && alembic upgrade head
uvicorn app.main:app --app-dir backend --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 配置模型

复制 `.env.example` 为 `.env`，至少配置：

- `EMBEDDING_API_KEY`：Embedding 模型密钥
- `LLM_API_KEY`：对话模型密钥

没有密钥时，可以把两个 provider 都设为 `dummy` 做离线演示，此时回答由本地规则生成，用于验证流程而非真实效果。

开启鉴权：

```dotenv
ENABLE_AUTH=true
API_KEYS=user-key-1,user-key-2
ADMIN_API_KEYS=admin-key-main
```

普通用户 Key 可以上传、提问；管理员 Key 可以删除文档。前端左侧“访问权限”输入 Key 后自动识别角色。

## 更换模型

### 更换 LLM

修改 `.env` 后重启后端即可：

```dotenv
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=sk-xxx
```

只要目标服务提供 OpenAI 兼容接口，就可以直接使用，包括 Qwen、GLM、Ollama 本地模型等。

### 更换 Embedding 模型

例如切换到 `text-embedding-v4`：

```dotenv
EMBEDDING_MODEL=text-embedding-v4
EMBEDDING_BASE_URL=https://your-provider.example.com/v1
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_DIM=1024
```

`EMBEDDING_DIM` 必须等于模型实际输出维度。重启后端后重建向量：

```bash
python backend/scripts/reembed_cli.py --recreate-table
```

如果只是换一个同维度的模型（例如同为 1536 维），可以不加 `--recreate-table`：

```bash
python backend/scripts/reembed_cli.py
```

## 使用流程

1. 打开前端，在左侧「知识库」上传 PDF / DOCX / MD / TXT。
2. 等待文档状态变为 `ready`。
3. 在对话框提问，例如「这份文档的核心流程是什么」。
4. 回答下方会展示引用来源，点击可查看原文片段。

## 常用 API

```bash
# 健康检查
curl http://localhost:8000/api/health

# 上传文档
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-API-Key: 你的Key" \
  -F "file=@doc.pdf"

# 发起问答
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 你的Key" \
  -d '{"question": "报销流程是什么？"}'
```

## CLI 工具

```bash
# 批量上传文档
python backend/scripts/ingest_cli.py ./docs/*.pdf --api-key 你的Key

# 运行评测
python backend/scripts/eval_cli.py backend/data/eval/sample.jsonl --api-key 你的Key
```
