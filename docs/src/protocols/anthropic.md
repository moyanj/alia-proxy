# Anthropic (Claude)

Anthropic 的 Claude 系列模型是强大的竞争者，但其 API 规范（特别是 Messages API）与 OpenAI 的存在显著差异。`AnthropicProvider` 的核心职责就是在这两种协议之间搭建一座无形的桥梁，让您可以像调用 OpenAI 模型一样无缝地使用 Claude。

## 核心转换逻辑

`AnthropicProvider` 在后台自动处理了以下所有复杂的转换工作：

### 1. 消息格式映射 (`_map_messages`)

- **System Prompt**: OpenAI 的 `system` 角色的消息被提取出来，并放入 Anthropic API 的顶级 `system` 字段中。
- **多模态内容**:
    - OpenAI 的图片格式: `{"type": "image_url", "image_url": {"url": "data:..."}}`
    - 会被自动转换为 Anthropic 的格式: `{"type": "image", "source": {"type": "base64", ...}}`
- **工具使用 (Tool Use)**:
    - **请求转换**:
        - OpenAI 的 `tool_calls`（来自 assistant）被转换为 Anthropic 的 `tool_use` 内容块。
        - OpenAI 的 `tool` 角色消息（包含工具调用的结果）被转换为 `user` 角色下的 `tool_result` 内容块。
    - **响应转换**:
        - Anthropic 响应中的 `tool_use` 块会被解析并重新组装成 OpenAI `tool_calls` 格式。
        - `finish_reason` 会被智能地设置为 `tool_calls` 或 `stop`。

### 2. 流式响应重写 (SSE)

这是最复杂的部分。Anthropic 的流式事件（Server-Sent Events）与 OpenAI 完全不同。

- **Anthropic 事件流**: `message_start`, `content_block_start`, `content_block_delta`, `message_delta`, `message_stop`。
- **`aiprox` 的工作**: `AnthropicProvider` 会实时监听这些事件，并在内存中进行重组，然后**伪装**成 OpenAI 格式的流式块 `data: {"choices": [{"delta": ...}]}` 发送给客户端。

**这个过程对客户端是完全透明的**。客户端的流式解析逻辑无需任何修改，就能像处理 OpenAI 的流一样处理来自 Claude 的响应。

### 3. API 请求参数映射

- `stop` -> `stop_sequences`
- `tool_choice` -> `tool_choice` (支持 `auto`, `any`, 和指定工具的转换)

## 配置

```toml
[providers.anthropic-claude]
type = "anthropic"
api_key = "sk-ant-xxxxxxxxxx"
# base_url 可选，默认为 "https://api.anthropic.com/v1"
```

- **`type = "anthropic"`**: 关键字段，指示 `ProviderFactory` 使用 `AnthropicProvider`。

## 支持原生接口

为了满足高级用户的需求，`aiprox` 也暴露了调用 Anthropic 原生接口的能力。

- **端点**: `POST /anthropic/v1/messages`
- **行为**: 当请求这个端点时，`aiprox` 会跳过大部分协议转换逻辑，直接将请求体（需符合 Anthropic 原生格式）转发给 Anthropic API。
- **保留的增强功能**: 即使在原生模式下，`aiprox` 依然会处理：
    - **多模态数据持久化**: 自动保存请求中的 Base64 图片。
    - **统一日志**: 请求和响应依然会被记录到数据库中。

这个原生端点为需要使用 Anthropic 特有高级功能（而 OpenAI 规范中没有对应项）的场景提供了灵活性。
