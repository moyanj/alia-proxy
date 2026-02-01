# 模型映射策略

除了简单的别名映射，`alia_proxy` 还支持将一个别名映射到**多个目标**，并提供了不同的流量分配策略。这为实现负载均衡、故障转移和成本优化提供了强大的工具。

## 多目标映射

您可以将一个别名映射到一个目标列表，而不是单个目标。

### 简写语法 (列表)

在 `config.toml` 的 `[mapping]` 部分，使用一个字符串数组：

```toml
[mapping]
# "chat-pool" 会在两个模型间轮询
chat-pool = ["openai-main/gpt-4o", "anthropic-pro/claude-3-opus-20240229"]
```

默认情况下，这种简写语法使用 `round-robin`（轮询）策略。

### 完整语法 (对象)

为了更精细地控制行为，您可以使用一个 TOML 表（table）来定义映射，并明确指定 `strategy`。

```toml
[mapping.smart-pool]
targets = [
    "openai-main/gpt-4o", 
    "anthropic-pro/claude-3-5-sonnet-20240620",
    "openai-backup/gpt-4-turbo"
]
strategy = "round-robin" # 或 "random"
```

当客户端请求 `"model": "smart-pool"` 时，`alia_proxy` 会根据指定的策略从 `targets` 列表中选择一个目标来处理请求。

## 支持的策略

### 1. 轮询 (Round-Robin)

- **关键字**: `round-robin`
- **行为**: 这是默认策略。`alia_proxy` 会按顺序将请求依次分配给 `targets` 列表中的每个目标。当到达列表末尾时，它会从头开始。
- **示例**:
    - 第 1 个请求 -> `openai-main/gpt-4o`
    - 第 2 个请求 -> `anthropic-pro/claude-3-5-sonnet-20240620`
    - 第 3 个请求 -> `openai-backup/gpt-4-turbo`
    - 第 4 个请求 -> `openai-main/gpt-4o`
    - ... 以此类推
- **适用场景**:
    - **负载均衡**: 将流量均匀地分散到多个具有相似能力和成本的模型或 API Key 上。
    - **分摊速率限制**: 如果您有多个 API Key，可以将它们配置为不同的 `provider` 实例，然后通过轮询来避免单个 Key 过快达到速率限制。

### 2. 随机 (Random)

- **关键字**: `random`
- **行为**: `alia_proxy` 会从 `targets` 列表中**随机选择一个**目标来处理每个请求。
- **适用场景**:
    - **无偏好分发**: 当您不关心请求的确切顺序，只想将流量随机打散到多个端点时。
    - **A/B 测试**: 随机地向用户提供由不同模型驱动的体验，以收集性能或质量数据。

## 故障自动降级 (Automatic Fallback)

`alia_proxy` 支持为映射配置**备选模型列表**（Fallbacks）。当主目标调用失败（如 API 宕机、速率限制或网络超时）时，系统会自动按顺序尝试备选列表中的模型，直到成功或全部失败。

### 配置方式

在 `config.toml` 的映射配置中添加 `fallbacks` 字段：

```toml
[mapping.gpt-high-availability]
# 首选目标
targets = ["openai-main/gpt-4o"]
# 降级列表：当 targets 失败时，依次尝试以下模型
fallbacks = [
    "anthropic-backup/claude-3-opus-20240229",
    "openai-backup/gpt-3.5-turbo"
]
strategy = "round-robin"
```

### 降级行为

1. 客户端请求 `model: "gpt-high-availability"`。
2. 系统首先根据 `targets` 和 `strategy` 选择主模型（例如 `openai-main/gpt-4o`）。
3. 如果主模型调用抛出异常（非 200 OK），系统会捕获该异常并记录日志。
4. 系统尝试 `fallbacks` 列表中的第一个模型（`anthropic-backup/claude-3-opus-20240229`）。
5. 如果成功，返回结果；如果再次失败，继续尝试下一个。
6. 如果所有 fallback 都失败，最终抛出最后一个异常。

> **注意**: 对于流式请求（Stream），降级仅在流建立阶段（即收到第一个数据块之前）有效。一旦流开始传输数据，为保证上下文完整性，后续的连接中断将不会触发重试。

## 内部实现说明

- **状态管理**: `alia_proxy` 在内存中为每个配置了 `round-robin` 策略的映射维护一个独立的计数器。这个计数器会随着每次请求递增，并确保了请求分发的顺序性。
- **无状态**: `random` 策略是无状态的，每次选择都是独立的。
- **热重载**: `config.toml` 的更改目前需要重启服务才能生效。
