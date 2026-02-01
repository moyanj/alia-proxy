# 核心架构

`alia_proxy` 采用前后端分离的现代化架构，后端基于 FastAPI，前端基于 Vue 3。整个系统被设计为高度模块化和可扩展的。

## 整体架构图

```mermaid
graph TD
    subgraph Client
        User[用户 / 客户端应用]
    end

    subgraph aiprox Service
        Router[Router 层 (FastAPI)]
        Service[Service 层]
        Provider[Provider 层]
        DB[(SQLite / PostgreSQL)]
        Media[本地媒体存储]
    end

    subgraph Upstream AI Providers
        OpenAI[OpenAI API]
        Anthropic[Anthropic API]
        Ollama[Ollama (本地)]
        Other[其他兼容 API]
    end

    User -- HTTP Request --> Router
    Router -- 调用 --> Service
    Service -- 编排 --> Provider
    Service -- 读写 --> DB
    Service -- 存储 --> Media
    Provider -- API Call --> OpenAI
    Provider -- API Call --> Anthropic
    Provider -- API Call --> Ollama
    Provider -- API Call --> Other
```

## 后端 (Backend)

后端使用 Python 和 FastAPI 构建，保证了高性能的异步处理能力。

### 1. Router 层 (`aiprox/routers`)

- **职责**: 暴露符合 OpenAI API 标准的 HTTP 端点，例如 `/v1/chat/completions`。
- **技术**: 使用 FastAPI 的 `APIRouter` 进行模块化管理。
- **特点**: 这一层非常“薄”，仅负责接收请求、基础校验，然后通过依赖注入将业务逻辑委托给 Service 层。它不包含任何具体的提供商逻辑。

### 2. Service 层 (`aiprox/services`)

- **职责**: 系统的业务逻辑核心。
- **`ProxyService`**: 请求的编排器。它负责解析模型名称、处理多模态数据（如 Base64 图片）、调用相应的 Provider、并在请求结束后触发日志记录。
- **`LoggerService`**: 异步日志记录服务。将请求的元数据（Token 消耗、延迟等）和详细内容（Prompt、Response）分别写入数据库，避免阻塞主请求流程。
- **`MediaService`**: 媒体文件处理服务。负责将图像、音频等二进制数据异步写入本地文件系统。

### 3. Provider 层 (`aiprox/providers`)

- **职责**: 实现策略模式，用于适配所有上游 AI 服务。
- **`BaseProvider`**: 定义所有提供商必须遵守的统一接口（如 `chat`, `stream` 等）。
- **具体实现**:
    - `OpenAIProvider`: 适用于 OpenAI 官方 API 及所有兼容其格式的服务（包括 Ollama）。
    - `AnthropicProvider`: 实现了 OpenAI 与 Anthropic 消息格式之间的双向转换，处理了两者在工具调用、多模态消息等方面的差异。
- **`ProviderFactory`**: 工厂类，根据配置文件和请求的模型名称，动态地实例化并缓存 Provider 对象。

### 4. 数据库 (Database)

- **技术**: 使用 `Tortoise-ORM`，一个异步的 ORM 库，与 FastAPI 的异步特性完美契合。
- **模型 (`aiprox/models.py`)**:
    - `RequestLog`: 存储请求的元数据，为高性能查询设计。
    - `RequestContent`: 独立存储大文本内容（Prompt/Response），避免主表膨胀。
    - `MediaResource`: 记录与请求关联的媒体文件信息。
- **默认数据库**: 使用 SQLite，方便快速启动。
- **生产数据库**: 通过 `AIPROX_DATABASE_URL` 环境变量可配置为 PostgreSQL、MySQL 等。
  - SQLite: `sqlite:///data/aiprox.db`
  - PostgreSQL: `postgres://user:password@host:5432/aiprox`
  - MySQL: `mysql://user:password@host:3306/aiprox`

## 前端 (Frontend)

前端是一个基于 Vue 3 的单页应用（SPA），提供了丰富的可视化和交互功能。

- **技术栈**:
    - **框架**: Vue 3 (Composition API + `<script setup>`)
    - **构建工具**: Vite
    - **状态管理**: Pinia
    - **UI 库**: TailwindCSS (Utility-First)
    - **图表**: ECharts
    - **图标**: Lucide Icons
- **主要视图 (`frontend/src/views`)**:
    - **Dashboard**: 概览页面，展示核心统计数据。
    - **Analytics**: 深入的用量分析图表。
    - **Logs**: 请求日志的查看、筛选和详情页。
    - **Playground**: 一个强大的在线工具，用于测试不同模型和参数。
    - **Providers / Mappings**: 用于管理和配置提供商和模型别名。
