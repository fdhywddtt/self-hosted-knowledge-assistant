# 企业知识库智能问答助手 完整使用说明

本项目是一个可自托管的企业知识库多智能体问答平台：上传文档后自动解析、切片、向量化入库，提问时按意图路由到智能体，结合混合检索和引用溯源生成回答。

## 1. 环境要求

| 组件 | 要求 |
| --- | --- |
| 操作系统 | Windows 10/11 或 Linux |
| Python | 3.11 或更高 |
| Node.js | 20 或更高 |
| PostgreSQL | 16 或更高 |
| pgvector 扩展 | 与 PostgreSQL 版本匹配 |
| Redis | 可选，未启动时自动降级不缓存 |

当前机器的 PostgreSQL 安装在 `E:\psql`，psql 命令路径为 `E:\psql\bin\psql.exe`。

## 2. 首次安装

### 2.1 准备数据库

用超级用户连接 PostgreSQL：

```powershell
E:\psql\bin\psql.exe -U postgres
```

创建项目账号和数据库：

```sql
CREATE USER assistant WITH PASSWORD 'assistant';
CREATE DATABASE assistant OWNER assistant;
```

切到项目数据库并创建 pgvector 扩展：

```sql
\c assistant
CREATE EXTENSION IF NOT EXISTS vector;
\dx
```

`\dx` 能看到 `vector` 即成功。

### 2.2 创建配置文件

```powershell
cd D:\model\智能体开发
Copy-Item .env.example .env
```

至少确认 `DATABASE_URL` 指向正确的数据库：

```text
DATABASE_URL=postgresql+asyncpg://assistant:assistant@localhost:5432/assistant
```

没有模型 API Key 时，保持 `EMBEDDING_PROVIDER=dummy` 和 `LLM_PROVIDER=dummy` 可离线演示。

### 2.3 安装后端依赖

```powershell
cd D:\model\智能体开发
python -m venv .venv
.\.venv\Scripts\pip.exe install -e "backend[dev]"
```

### 2.4 安装前端依赖

```powershell
cd D:\model\智能体开发\frontend
npm install
npm approve-scripts esbuild
npm rebuild esbuild
```

`esbuild` 是 Vite 的构建组件，最后两条命令用于生成它的原生二进制，否则启动会报 `spawn EPERM`。

### 2.5 初始化数据库表

```powershell
cd D:\model\智能体开发\backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

成功后会创建 `documents`、`chunks`、`conversations`、`messages` 四张表、HNSW 向量索引和全文索引。

## 3. 启动与停止

启动顺序：先后端，后前端。

### 3.1 启动后端

```powershell
cd D:\model\智能体开发\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

验证：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

返回 `status: ok` 即正常。

### 3.2 启动前端

```powershell
cd D:\model\智能体开发\frontend
npm run dev
```

浏览器打开 http://localhost:5173 。

### 3.3 停止

- 后端：在运行后端的终端按 `Ctrl+C`。
- 前端：在运行前端的终端按 `Ctrl+C`。
- 端口被占用时可用 `netstat -ano | findstr :8000` 找到 PID，再 `taskkill /PID <PID> /F`。

## 4. 配置说明（.env）

| 配置项 | 说明 |
| --- | --- |
| `DATABASE_URL` | PostgreSQL 连接地址 |
| `EMBEDDING_PROVIDER` | `openai` 或 `dummy` |
| `EMBEDDING_MODEL` | Embedding 模型名，如 `text-embedding-v4` |
| `EMBEDDING_DIM` | 向量维度，必须等于模型实际输出维度 |
| `EMBEDDING_BASE_URL` | OpenAI 兼容接口地址 |
| `EMBEDDING_API_KEY` | Embedding API 密钥 |
| `LLM_PROVIDER` | `openai` 或 `dummy` |
| `LLM_MODEL` | 对话模型名，如 `gpt-4o-mini`、`deepseek-chat` |
| `LLM_BASE_URL` / `LLM_API_KEY` | 对话模型接口地址与密钥 |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 文档切片大小与重叠 |
| `TOP_K` / `RERANK_TOP_K` | 召回数量与重排后数量 |
| `RERANKER_PROVIDER` | `rrf` 或 `cross-encoder` |
| `ENABLE_AUTH` / `API_KEYS` | 开启 API Key 鉴权 |
| `ADMIN_API_KEYS` | 管理员 Key，可删除文档，逗号分隔 |
| `CORS_ORIGINS` | 允许的前端地址 |

修改 `.env` 后需要重启后端生效。

## 5. 日常使用

### 5.1 上传文档

支持格式：PDF、DOCX、Markdown、TXT。

网页左侧“知识库”点击上传按钮选择文件。文档状态：

| 状态 | 含义 |
| --- | --- |
| uploaded | 已上传，等待处理 |
| processing | 正在解析和向量化 |
| ready | 可检索 |
| failed | 处理失败，可查看 error |

### 5.2 提问

点击“新建对话”，输入问题后回车。回答下方会显示引用来源，包括文件名、页码（PDF）和原文片段。

示例问题：

- “报销流程是什么？”
- “总结一下员工手册”
- “请假超过三天需要谁审批？”

### 5.3 会话管理

左侧可切换历史会话，点击“新建对话”开启新会话。

## 6. API 说明

基础地址：`http://127.0.0.1:8000`，接口文档：`http://127.0.0.1:8000/docs`。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| POST | `/api/v1/documents/upload` | 上传文档（multipart，字段名 `file`） |
| GET | `/api/v1/documents` | 文档列表 |
| GET | `/api/v1/documents/{id}` | 文档详情 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 |
| POST | `/api/v1/chat` | 发起问答 |
| GET | `/api/v1/conversations` | 会话列表 |
| GET | `/api/v1/conversations/{id}/messages` | 会话消息 |
| GET | `/api/v1/agents` | 智能体列表 |
| GET | `/api/v1/me` | 当前 Key 的角色（admin / user） |

问答请求示例：

```powershell
$body = '{"question":"报销流程是什么？"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/chat `
  -Method Post -ContentType 'application/json; charset=utf-8' -Body $body | ConvertTo-Json -Depth 6
```

开启鉴权后，所有 `/api/v1` 请求需要请求头 `X-API-Key`。

## 7. 命令行工具

### 7.1 批量上传文档

```powershell
cd D:\model\智能体开发
.\.venv\Scripts\python.exe backend\scripts\ingest_cli.py D:\docs\guide.pdf D:\docs\handbook.md
```

开启鉴权后加上你的 Key：

```powershell
.\.venv\Scripts\python.exe backend\scripts\ingest_cli.py D:\docs\guide.pdf --api-key 你的Key
```

### 7.2 运行评测

```powershell
.\.venv\Scripts\python.exe backend\scripts\eval_cli.py backend\data\eval\sample.jsonl `
  --base-url http://127.0.0.1:8000
```

开启鉴权后加 `--api-key 你的Key`。

### 7.3 重建向量

```powershell
.\.venv\Scripts\python.exe backend\scripts\reembed_cli.py
```

Embedding 模型维度变化时：

```powershell
.\.venv\Scripts\python.exe backend\scripts\reembed_cli.py --recreate-table
```

## 8. 测试与代码检查

```powershell
cd D:\model\智能体开发\backend
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe -m ruff check app tests
```

## 9. 更换模型

### 9.1 更换 LLM

示例改为 DeepSeek：

```dotenv
LLM_PROVIDER=openai
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=sk-xxx
```

只要是 OpenAI 兼容接口即可，Qwen、GLM、Ollama 同理。

### 9.2 更换 Embedding

示例改为 `text-embedding-v4`：

```dotenv
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-v4
EMBEDDING_BASE_URL=https://your-provider.example.com/v1
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_DIM=1024
```

`EMBEDDING_DIM` 必须等于模型实际输出维度。修改后重启后端并重建向量：

```powershell
.\.venv\Scripts\python.exe backend\scripts\reembed_cli.py --recreate-table
```

如果只是换同维度模型，可不加 `--recreate-table`。

## 10. 数据查看与清理

### 10.1 查看数据

```powershell
E:\psql\bin\psql.exe -U assistant -d assistant
```

```sql
SELECT id, filename, status, created_at FROM documents;
SELECT count(*) FROM chunks;
SELECT id, role, left(content, 80) FROM messages ORDER BY created_at DESC LIMIT 20;
```

中文乱码时先执行：

```sql
SET client_encoding TO 'UTF8';
```

### 10.2 删除文档

网页：知识库列表右侧垃圾桶按钮。

API：

```powershell
curl.exe -X DELETE http://127.0.0.1:8000/api/v1/documents/<文档ID>
```

### 10.3 清空业务数据

```sql
TRUNCATE documents, conversations CASCADE;
```

### 10.4 完全重置

```powershell
cd D:\model\智能体开发\backend
..\.venv\Scripts\python.exe -m alembic downgrade base
..\.venv\Scripts\python.exe -m alembic upgrade head
```

### 10.5 备份

```powershell
E:\psql\bin\pg_dump.exe -U assistant -d assistant -F c -f D:\backup\assistant.dump
```

上传的原始文件存放在 `D:\model\智能体开发\data\documents`，删除数据库记录不会自动删除这些文件，彻底清理时手动处理。

## 11. 常见问题

| 现象 | 解决方法 |
| --- | --- |
| 前端报 `spawn EPERM` | 在 `frontend` 目录执行 `npm approve-scripts esbuild` 和 `npm rebuild esbuild` |
| 迁移报权限不足创建扩展 | 用 `postgres` 超级用户在 `assistant` 库执行 `CREATE EXTENSION IF NOT EXISTS vector;` |
| 页面能开但接口报错 | 确认后端已启动且端口是 8000 |
| 控制台中文乱码 | 是 PowerShell 显示编码问题，接口数据本身正常 |
| 端口被占用 | `netstat -ano | findstr :8000` 查 PID 后 `taskkill /PID <PID> /F` |
| Redis 没装 | 不影响运行，Embedding 缓存自动降级 |

## 12. 权限与对外部署

### 12.1 两级 API Key

- `API_KEYS`：普通用户 Key，可以上传文档、提问、查看会话，不能删除。
- `ADMIN_API_KEYS`：管理员 Key，拥有全部权限，包括删除文档。
- `ENABLE_AUTH=false` 时不做鉴权，所有人都是管理员，只用于本地开发。

示例：

```dotenv
ENABLE_AUTH=true
API_KEYS=user-key-1,user-key-2
ADMIN_API_KEYS=admin-key-main
```

开启后，前端在左侧“访问权限”输入 Key 并保存，浏览器会记住；普通用户不显示删除按钮，管理员显示。

### 12.2 生产模式开关

- `DEBUG=false` 时自动关闭 `/docs`、`/redoc`、`/openapi.json`。
- 后端只监听本机：`uvicorn app.main:app --host 127.0.0.1 --port 8000`。
- 前端构建后用 Nginx 托管，配置样例见 `deploy/nginx.conf.example`，监听 8090 并代理 `/api`。

### 12.3 上线清单

- [ ] 修改数据库密码并同步 `.env`
- [ ] `ENABLE_AUTH=true` 并发放 Key
- [ ] 后端只监听 127.0.0.1
- [ ] Nginx 监听 8090，只开放该端口
- [ ] 防火墙只放行 8090 给指定内网 IP 段
- [ ] 公网环境配置 HTTPS
- [ ] 定期备份数据库

## 13. 项目结构

```text
.
├── backend/
│   ├── app/agents/       # 智能体与意图路由
│   ├── app/api/          # API 路由
│   ├── app/core/         # 配置、安全、日志
│   ├── app/db/           # 模型与会话
│   ├── app/services/     # 解析、检索、Embedding、记忆
│   ├── migrations/       # 数据库迁移
│   ├── scripts/          # 上传、评测、重建 CLI
│   └── tests/            # 单元测试
├── frontend/             # React 前端
├── docs/                 # 文档
└── .env                  # 本地配置（不提交）
```
