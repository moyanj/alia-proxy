# OpenAI 兼容

`OpenAIProvider` 是 `aiprox` 中最基础也是最核心的 Provider 实现。它不仅用于连接 OpenAI 官方的 API，也适用于任何**兼容 OpenAI API V1 规范**的第三方服务或本地模型。

## 功能

`OpenAIProvider` 实现了 `BaseProvider` 定义的所有标准接口：

- **聊天补全**: `POST /v1/chat/completions` (支持流式和非流式)
- **嵌入生成**: `POST /v1/embeddings`
- **图像生成**: `POST /v1/images/generations`
- **文本转语音**: `POST /v1/audio/speech`
- **模型列表**: `GET /v1/models`

## 配置

在 `config.toml` 中，一个典型的 OpenAI 兼容提供商配置如下：

```toml
[providers.openai-official]
type = "openai"
api_key = "sk-xxxxxxxxxxxxxxxxxxx"
# base_url 是可选的，默认指向 "https://api.openai.com/v1"
base_url = "https://api.openai.com/v1" 
timeout = 60.0 # 可选，自定义请求超时时间（秒）
```

- **`type = "openai"`**: 这是必需的，它告诉 `ProviderFactory` 使用 `OpenAIProvider` 类来实例化这个提供商。
- **`api_key`**: 您的 API 密钥。
- **`base_url`**: API 的根地址。您可以将其指向任何兼容的端点。
- **`timeout`**: 可选参数，用于设置 `httpx` 客户端的请求超时时间。

## 隐式行为

- **流式 Usage 注入**: 当您发起一个流式聊天请求 (`"stream": true`) 时，`OpenAIProvider` 会自动在请求体中添加 `"stream_options": {"include_usage": true}`。这样做是为了确保即使在流式响应的最后一个数据块中，也能收到来自 OpenAI 的 `usage` 字段，从而精确地记录本次请求的 Token 消耗。这对于成本分析和用量监控至关重要。

## 适用场景

`OpenAIProvider` 的应用范围非常广泛：

1.  **OpenAI 官方服务**: 直接连接 `https://api.openai.com/v1`。
2.  **Azure OpenAI**: 将 `base_url` 指向您的 Azure OpenAI 部署地址。
3.  **第三方代理服务**: 许多第三方服务提供了兼容 OpenAI 格式的 API，您可以将 `base_url` 指向它们。
4.  **本地模型 (Ollama, LM Studio等)**: 正如 [Ollama](./ollama.md) 章节所述，这些本地模型框架通常会提供一个 OpenAI 兼容的接口，可以直接与 `OpenAIProvider` 对接。
