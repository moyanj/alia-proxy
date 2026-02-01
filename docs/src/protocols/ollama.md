# Ollama

[Ollama](https://ollama.com/) 是目前最流行的本地 LLM 运行框架之一。由于 Ollama 原生提供了 OpenAI 兼容的 API 接口，`aiprox` 可以零成本地接入 Ollama，将其作为本地推理后端。

## 原理

`aiprox` 并没有为 Ollama 编写单独的 Provider 类，而是直接复用 `OpenAIProvider`。通过配置 `base_url` 指向 Ollama 的本地服务端口（默认 `11434`），`aiprox` 就可以像调用 OpenAI 一样调用本地模型。

## 配置指南

假设您的 Ollama 服务运行在本地的 `11434` 端口。

### 1. 确保 Ollama 正在运行

```bash
ollama serve
# 或者
ollama run llama3
```

### 2. 修改 config.toml

添加一个新的 provider 节点：

```toml
[providers.ollama-local]
type = "openai"  # 注意：这里使用 "openai" 类型，因为协议是兼容的
base_url = "http://localhost:11434/v1" # 指向 Ollama 的 OpenAI 兼容端点
api_key = "ollama" # Ollama 不需要真实的 Key，但为了通过校验，可以填任意非空字符串
```

## 使用方法

现在，您可以通过 `aiprox` 调用 Ollama 中的任何模型。

**示例请求**:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama-local/llama3",
    "messages": [{"role": "user", "content": "为什么天空是蓝色的？"}]
  }'
```

- **`ollama-local`**: 对应配置文件中的 `[providers.ollama-local]`。
- **`llama3`**: 您在 Ollama 中已经 pull 下来的模型名称。

## 优势

将 Ollama 接入 `aiprox` 后，您将获得以下增强体验：

- **统一日志**: 本地模型的调用记录也会被完整保存到数据库，并可在仪表盘中查看。
- **API Key 管理**: 虽然 Ollama 本身不鉴权，但通过 `aiprox` 暴露服务后，您可以利用 `aiprox` 未来的鉴权机制来保护本地接口。
- **混合部署**: 您可以在同一个应用中混合使用昂贵的云端模型（如 GPT-4）和廉价的本地模型（如 Llama 3），只需切换 `model` 参数即可。
