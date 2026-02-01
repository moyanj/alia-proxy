# AliaProxy - 统一 AI API 代理服务

<p align="center">
  <a href="https://github.com/moyanj/alia-proxy/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://github.com/moyanj/alia-proxy/actions"><img src="https://img.shields.io/github/actions/workflow/status/moyanj/alia-proxy/docs.yml?label=docs" alt="Docs CI"></a>
  <img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/node-20+-green.svg" alt="Node 20+">
  <a href="https://moyanj.github.io/alia-proxy/"><img src="https://img.shields.io/badge/docs-online-blue.svg" alt="Documentation"></a>
</p>

<p align="center">
  统一的多提供商 AI API 代理服务，支持日志记录、Web 仪表盘和多数据库。
</p>

<p align="center">
  <a href="./README_EN.md">English</a> | 简体中文
</p>

## 功能特性

- **多提供商支持**：OpenAI、Anthropic、Ollama 以及其他兼容 OpenAI API 格式的服务。
- **动态路由**：使用 `provider/model` 格式路由请求（例如 `gpt4-main/gpt-4o`）。
- **高可用性**：主模型失败时自动降级到备选模型/提供商。
- **多媒体支持**：图像生成 (`/v1/images/generations`) 和语音合成 (`/v1/audio/speech`)。
- **本地媒体存储**：媒体文件保存到 `data/media/` 并通过认证 API 提供服务。
- **统一日志记录**：所有请求和响应（包括媒体路径）记录到数据库。
- **导出系统**：支持导出日志为 ShareGPT JSONL 或 CSV 格式。
- **Web 仪表盘**：实时查看统计数据、日志和多媒体输出。
- **多数据库支持**：SQLite（默认）、PostgreSQL、MySQL。

## 项目结构

```
/
├── alia_proxy/           # 后端 FastAPI 应用
│   ├── providers/        # 提供商策略实现
│   ├── routers/          # API 端点
│   ├── services/         # 核心业务逻辑（日志、媒体）
│   ├── models.py         # 数据库模型
│   └── main.py           # 应用入口
├── frontend/             # Vue.js 仪表盘
├── data/                 # 持久化存储（SQLite、媒体文件）
├── config.toml           # 提供商配置
├── docker-compose.yml    # 容器编排
├── Dockerfile            # 单一 Dockerfile（前端+后端）
└── docs/                 # mdBook 文档
```

## 快速开始

### 使用 Docker（推荐）

最简单的启动方式，前后端合并为单一容器。

1. **配置提供商**：
   ```bash
   cp config.example.toml config.toml
   # 编辑 config.toml 添加 API 密钥
   ```

2. **配置环境变量**（可选）：
   ```bash
   cp .env.example .env
   # 编辑 .env 自定义数据库、调试模式等
   ```

3. **启动服务**：
   ```bash
   docker-compose up -d
   ```

4. **访问应用**：
   - **Web 仪表盘**: http://localhost:8000
   - **API 服务**: http://localhost:8000/v1/...

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ALIA_DATABASE_URL` | `sqlite:///data/alia.db` | 数据库连接字符串，支持 SQLite、PostgreSQL、MySQL |
| `ALIA_MEDIA_DIR` | `/app/data/alia-media` | 媒体文件存储目录 |
| `ALIA_DEBUG` | `false` | 启用调试模式 |
| `ALIA_HOT_RELOAD` | `false` | 启用 config.toml 热重载 |

### 使用 PostgreSQL 替代 SQLite

1. 编辑 `.env`：
   ```bash
   ALIA_DATABASE_URL=postgres://user:password@host:5432/alia
   ```

2. 取消 `docker-compose.yml` 中 `postgres` 服务的注释

## 手动安装（开发环境）

### 后端

```bash
# 安装依赖
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml

# 运行
cp config.example.toml config.toml
uv run python -m alia_proxy.main
```

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```

## API 使用示例

聊天完成示例：
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt4-main/gpt-4o",
    "messages": [{"role": "user", "content": "你好！"}]
  }'
```

## 文档

- [在线文档](https://moyanj.github.io/alia-proxy/)
- [English Documentation](./README_EN.md)
- 完整文档位于 `docs/` 目录

## 许可证

MIT License
