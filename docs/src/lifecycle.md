# 请求生命周期

理解一个请求在 `aiprox` 系统内部的完整流转过程，有助于更好地排查问题和进行二次开发。下面我们以一个包含图片的流式聊天请求为例，追踪其完整的生命周期。

**请求示例**:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "smart-claude/claude-3-5-sonnet-20240620",
    "messages": [
      {
        "role": "user",
        "content": [
          { "type": "text", "text": "描述一下这张图片" },
          { 
            "type": "image_url",
            "image_url": { "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..." }
          }
        ]
      }
    ],
    "stream": true
  }'
```

---

### 1. 进入 Router 层

- **接收**: FastAPI 接收到 `POST /v1/chat/completions` 请求。
- **依赖注入**: 请求被路由到 `aiprox/routers/openai.py` 中的 `chat_completions` 函数。该函数的关键依赖 `proxy: ProxyService = Depends(get_proxy_service)` 被触发。

### 2. 解析与实例化 (deps.py)

- **`get_proxy_service`** 开始工作：
    1.  从请求体中提取 `"model": "smart-claude/claude-3-5-sonnet-20240620"`。
    2.  调用 `ProviderFactory.resolve_model()` 方法解析此字段。
    3.  `ProviderFactory` 发现 `smart-claude` 是一个在 `config.toml` 中定义的别名，假设它指向 `anthropic-main` 实例。
    4.  最终解析出 `instance_name = "anthropic-main"` 和 `actual_model = "claude-3-5-sonnet-20240620"`。
    5.  `ProviderFactory` 检查是否存在 `anthropic-main` 的缓存实例。如果没有，则根据配置创建一个 `AnthropicProvider` 实例并缓存。
    6.  `ProxyService` 被实例化，并注入了 Provider 实例、模型名称和客户端 IP 地址。
    7.  `get_proxy_service` 执行完毕，`ProxyService` 实例被传递给 Router 函数。

### 3. Service 层预处理

- **调用 `proxy.chat_stream()`**: 由于请求中 `"stream": true`，Router 调用了 `chat_stream` 方法。
- **媒体内容拦截**:
    1.  `_process_messages_for_log` 方法被调用。
    2.  它遍历 `messages` 列表，发现一个 Base64 格式的图片。
    3.  `MediaService` (`save_media`) 被调用，将解码后的图片二进制数据异步写入 `data/media/` 目录，并生成一个唯一文件名，例如 `f8e2c1b0-....jpeg`。
    4.  原始的 Base64 字符串在内存中被替换为一个占位符，如 `[IMAGE: f8e2c1b0-....jpeg]`。这个清洗过后的 prompt 用于后续的日志记录。
    5.  同时，原始的 Base64 数据依然会传递给 Provider，用于发送给上游服务。

### 4. Provider 层适配与转发

- **`AnthropicProvider.stream()`** 被调用。
- **协议转换**:
    1.  它将 OpenAI 格式的 `messages` 列表（包括 `image_url`）转换为 Anthropic Messages API 所要求的格式。例如，`image_url` 被转换为 `{"type": "image", "source": ...}` 结构。
    2.  构造包含 `x-api-key` 和 `anthropic-version` 的请求头。
    3.  使用 `httpx.AsyncClient` 向 Anthropic API 发起流式 POST 请求。

### 5. 流式响应处理

- **接收 SSE**: `aiprox` 开始接收来自 Anthropic 的 Server-Sent Events (SSE)。
- **实时协议重写**:
    1.  `AnthropicProvider` 逐行解析事件流（如 `message_start`, `content_block_delta`）。
    2.  **实时地**将这些 Anthropic 特有的事件**重写**为 OpenAI 兼容的流式块格式，即 `data: {"id": ..., "choices": [{"delta": ...}]}`。
    3.  这些重写后的数据块通过 `yield` 返回给 `ProxyService`。
- **透传**: `ProxyService` 将这些数据块直接 `yield` 给 FastAPI 的 `StreamingResponse`，后者再将其发送给客户端。客户端收到的体验与直接请求 OpenAI 完全一致。

### 6. Service 层后处理与日志记录

- **流结束**: 当从上游接收到 `[DONE]` 或等效的结束信号后，`chat_stream` 方法的循环终止。
- **异步日志记录**:
    1.  此时，`ProxyService` 已经收集到了完整的响应内容 `full_content` 和从流末尾块中解析出的 `usage`（Token 消耗）。
    2.  调用 `LoggerService` (`log_request`)，将所有信息（清洗后的 prompt、完整响应、Token 统计、延迟、IP、关联的媒体文件路径 `f8e2c1b0-....jpeg` 等）作为一个任务提交。
    3.  `log_request` 使用 `Tortoise-ORM` 异步地将这些信息写入 `RequestLog`, `RequestContent` 和 `MediaResource` 这三张表中。

**至此，整个请求的生命周期结束。关键点在于，日志记录和媒体存储等 I/O 密集型操作都是异步执行的，并且发生在主响应流程之后，确保了对用户请求的低延迟响应。**
