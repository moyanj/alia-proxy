# 快速开始

本章节将引导您完成 `aiprox` 的安装、配置和首次请求。

## 环境要求

在开始之前，请确保您的开发环境中已安装以下工具：

- **Docker & Docker Compose**: 推荐用于生产环境和一键部署。
- **Python 3.10+**: 后端服务运行环境。推荐使用 `uv` 进行包管理。
- **Node.js 20+**: 前端开发环境。推荐使用 `pnpm` 进行包管理。

## 推荐方式：使用 Docker

这是最简单、最快捷的启动方式，适用于所有操作系统。

1.  **克隆项目**:
    ```bash
    git clone https://github.com/moyanj/aiprox.git
    cd aiprox
    ```

2.  **配置提供商**:
    复制配置文件模板：
    ```bash
    cp config.example.toml config.toml
    ```
    然后编辑 `config.toml` 文件，填入您的 AI 提供商 API 密钥。例如：
    ```toml
    [providers.openai-main]
    type = "openai"
    api_key = "sk-..." 
    ```

3.  **启动服务**:
    使用 Docker Compose 一键启动后端、前端和数据库容器。
    ```bash
    docker-compose up --build
    ```

4.  **访问应用**:
    - **Web 仪表盘**: [http://localhost:3000](http://localhost:3000)
    - **API 服务**: `http://localhost:8000`

## 手动安装（适用于开发）

如果您希望对项目进行二次开发，可以手动启动前后端服务。

### 启动后端

1.  **安装依赖**:
    我们使用 `uv` 进行 Python 环境和包管理。
    ```bash
    # 创建虚拟环境
    uv venv
    
    # 激活虚拟环境
    source .venv/bin/activate
    
    # 安装依赖
    uv pip install -r requirements.txt
    ```

2.  **配置**:
    同样，复制并编辑 `config.toml` 文件。

3.  **启动后端服务**:
    ```bash
    uv run python -m aiprox.main
    ```
    服务将在 `http://localhost:8000` 启动。

### 启动前端

1.  **进入前端目录**:
    ```bash
    cd frontend
    ```

2.  **安装依赖**:
    我们使用 `pnpm` 作为包管理器。
    ```bash
    pnpm install
    ```

3.  **启动前端开发服务**:
    ```bash
    pnpm dev
    ```
    服务将在 `http://localhost:3000` 启动，并具备热重载功能。

## 发送您的第一个请求

无论使用何种方式启动，您都可以通过以下 `curl` 命令向 `aiprox` 发送一个聊天请求：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai-main/gpt-4o",
    "messages": [{"role": "user", "content": "你好，aiprox！"}]
  }'
```

**注意**: 请将 `"model"` 字段中的 `"openai-main"` 替换为您在 `config.toml` 中配置的提供商实例名。

现在，您可以访问 [http://localhost:3000/logs](http://localhost:3000/logs) 查看刚刚发出的请求日志了！
