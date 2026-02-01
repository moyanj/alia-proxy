# 动态路由与别名

`aiprox` 最核心的功能之一是其强大的动态路由能力。它允许您通过一个统一的入口，将请求智能地分发到任何后端配置的 AI 提供商，而无需修改客户端代码。

## 基本路由格式

`aiprox` 遵循一个简单而直观的路由格式：

```
<provider_instance_name>/<model_identifier>
```

这个格式被用在所有符合 OpenAI 标准的 API 请求的 `model` 字段中。

- **`provider_instance_name`**: 这是您在 `config.toml` 文件中为某个提供商配置的唯一名称（键名）。例如 `openai-main`, `anthropic-backup`, `local-ollama`。
- **`model_identifier`**: 这是该提供商所支持的实际模型名称，例如 `gpt-4o`, `claude-3-5-sonnet-20240620`, `llama3`。

### 示例

假设您的 `config.toml` 配置如下：

```toml
[providers.openai-us-east]
type = "openai"
api_key = "sk-..."

[providers.anthropic-sonnet]
type = "anthropic"
api_key = "sk-ant-..."
```

您可以这样发送请求：

- **请求 OpenAI**:
  ```json
  {
    "model": "openai-us-east/gpt-4o",
    "messages": [...]
  }
  ```

- **请求 Anthropic**:
  ```json
  {
    "model": "anthropic-sonnet/claude-3-5-sonnet-20240620",
    "messages": [...]
  }
  ```

系统会自动解析 `model` 字段，找到名为 `anthropic-sonnet` 的配置，实例化对应的 `AnthropicProvider`，然后将 `claude-3-5-sonnet-20240620`作为实际模型名传递给它。

## 模型别名 (Alias)

为了进一步提高灵活性并解耦客户端与后端配置，`aiprox` 支持强大的模型别名系统。您可以在 `config.toml` 中定义一个或多个别名，将一个简单的名称映射到一个具体的 `provider/model` 目标。

### 定义别名

在 `config.toml` 中添加 `[mapping]` 部分：

```toml
# ... providers 配置 ...

[mapping]
# 将 "gpt4" 这个别名映射到具体的提供商和模型
gpt4 = "openai-us-east/gpt-4o"

# 定义一个更通用的别名
smartest-model = "anthropic-sonnet/claude-3-5-sonnet-20240620"
```

### 使用别名

现在，客户端可以直接使用这个简短的别名，而无需关心底层的具体实现：

```json
{
  "model": "gpt4",
  "messages": [...]
}
```

`aiprox` 在处理请求时，会首先检查 `model` 字段是否匹配 `mapping` 中的任何一个键。如果匹配，它会自动将请求路由到 `openai-us-east/gpt-4o`。

### 别名的优势

- **抽象化**: 客户端代码变得更加简洁和稳定。
- **无缝切换**: 如果您想将所有使用 `gpt4` 别名的流量切换到另一个模型（甚至是另一个提供商），只需修改 `config.toml` 中 `mapping` 的一行配置即可，无需重新部署任何客户端应用。
- **A/B 测试**: 您可以快速更改别名指向，轻松实现不同模型之间的 A/B 测试。
