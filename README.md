# Self-Hosted Knowledge Assistant

一个可自托管、面向企业场景的多智能体知识库问答平台。上传文档后，系统会自动解析、切片、向量化并入库；提问时按意图路由到对应智能体，结合混合检索与引用溯源生成可追溯的回答。

## 核心特性

- 文档接入：PDF、DOCX、Markdown、TXT
- RAG 管线：解析 -> 分块 -> Embedding -> 混合检索（向量 + 全文）-> 重排 -> 引用
- 多智能体：意图路由、知识问答、文档总结，支持继续扩展
- 会话记忆：对话持久化、上下文续聊
- 两级权限：普通用户可上传提问，管理员可删除文档
- 生产安全：`DEBUG=false` 自动关闭接口文档，Nginx 生产部署
- 可评测：黄金问答集 + 检索召回 + LLM 裁判
- 一键部署：Docker Compose，前端 + 后端 + 数据库 + 缓存
- 模型可切换：兼容 OpenAI 及任何 OpenAI 兼容接口，支持 `text-embedding-v4`、DeepSeek、Qwen、GLM、Ollama 等

## 技术栈

| 模块 | 选型 |
| --- | --- |
| 后端框架 | FastAPI + Uvicorn |
| 编排 | 轻量多智能体路由，支持按业务场景扩展 |
| ORM / 迁移 | SQLAlchemy 2 + Alembic |
| 数据库 | PostgreSQL + pgvector |
| 缓存 | Redis |
| Embedding / LLM | OpenAI 兼容 HTTP 客户端，可插拔 Provider |
| 文档解析 | pypdf、python-docx |
| 前端 | React + Vite + TypeScript |
| 部署 | Docker Compose、Nginx |
| 评测 / 测试 | pytest、LLM-as-Judge |

## 快速开始

```bash
cp .env.example .env
docker compose up --build
```

然后打开 http://localhost:8080 。详细步骤见 [docs/quickstart.md](docs/quickstart.md)。

## 权限模型

开启 `ENABLE_AUTH=true` 后：

| Key | 角色 | 权限 |
| --- | --- | --- |
| `API_KEYS` | 普通用户 | 上传文档、提问、查看会话 |
| `ADMIN_API_KEYS` | 管理员 | 以上权限 + 删除文档 |

前端左侧“访问权限”输入 Key 后自动识别角色，普通用户不显示删除按钮。本地开发可保持 `ENABLE_AUTH=false` 全开放。

## 生产部署

- Docker Compose：数据库账号密码从 `.env` 读取，见 `docker-compose.yml`
- Nginx 生产配置样例：`deploy/nginx.conf.example`
- 后端只监听 `127.0.0.1`，对外只开放前端端口
- 完整上线清单见 [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

## 项目结构

```text
.
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── agents/          # 智能体：知识问答、文档总结、意图路由
│   │   ├── api/             # API 路由
│   │   ├── core/            # 配置、安全、日志
│   │   ├── db/              # SQLAlchemy 模型与会话
│   │   ├── schemas/         # Pydantic 模型
│   │   └── services/        # 解析、分块、检索、Embedding、记忆
│   ├── migrations/          # Alembic 迁移
│   ├── scripts/             # 上传、评测、重建向量 CLI
│   └── tests/               # 单元测试
├── frontend/                # React 前端
├── docs/                    # 架构、快速开始、评测、使用说明
├── deploy/                  # Nginx 生产配置样例
├── docker-compose.yml
└── .env.example
```

## 文档

- [架构设计](docs/architecture.md)
- [快速开始](docs/quickstart.md)
- [评测体系](docs/evaluation.md)
- [完整使用说明](docs/USER_GUIDE.md)

## 许可证

MIT
