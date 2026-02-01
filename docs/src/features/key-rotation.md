# API Key 轮换

`alia_proxy` 内置了一个强大且对用户透明的 API Key 轮换机制。这个功能允许您为一个提供商配置**多个 API Key**，系统会自动在这些 Key 之间进行轮询，从而有效地分摊流量、提高请求成功率并绕开单个 Key 的速率限制。

这是一个**隐式行为**，意味着您无需在请求中指定使用哪个 Key，`alia_proxy` 会在后台自动处理。

## 如何配置

在 `config.toml` 文件中，将任意一个 provider 配置的 `api_key` 字段从单个字符串改为一个**字符串数组**即可。

### 单 Key 配置 (标准)

```toml
[providers.openai-main]
type = "openai"
api_key = "sk-xxxxxxxxxxxxxxxxxxx"
```

### 多 Key 配置 (轮换)

```toml
[providers.openai-pool]
type = "openai"
# 提供一个 API Key 列表
api_key = [
    "sk-key-one-xxxxxxxxxxxx",
    "sk-key-two-yyyyyyyyyyyy",
    "sk-key-three-zzzzzzzzzzzz"
]
```

## 工作原理

当 `alia_proxy` 的 `ProviderFactory` 加载 `openai-pool` 这个配置时，它会检测到 `api_key` 是一个列表。随后，该 `OpenAIProvider` 实例内部会维护一个**索引计数器**。

1.  **第一个请求**到达，使用 `"model": "openai-pool/gpt-4o"`。
    - Provider 实例返回列表中的第 0 个 Key (`sk-key-one-...`)。
    - 内部计数器增加到 1。

2.  **第二个请求**到达。
    - Provider 实例返回列表中的第 1 个 Key (`sk-key-two-...`)。
    - 内部计数器增加到 2。

3.  **第三个请求**到达。
    - Provider 实例返回列表中的第 2 个 Key (`sk-key-three-...`)。
    - 内部计数器增加到 3。

4.  **第四个请求**到达。
    - 计数器通过取模运算 (`3 % 3`) 回到 0。
    - Provider 实例再次返回第 0 个 Key (`sk-key-one-...`)。

这个过程会无限循环下去，确保了所有 API Key 被均匀地使用。

## 优势与应用场景

- **提高吞吐量**: 如果您的服务商对单个 API Key 的 QPS（每秒查询数）或 RPM（每分钟请求数）有限制，使用多个 Key 可以将总吞吐量提升 N 倍（N 为 Key 的数量）。

- **增强健壮性**: 即使某个 Key 因为账单问题或被封禁而失效，轮换机制可以确保后续请求能继续使用其他有效的 Key，从而降低了单点故障的风险（注意：`alia_proxy` 目前没有内置自动检测并移除失效 Key 的功能，失效的 Key 依然会参与轮换并导致部分请求失败）。

- **成本分摊**: 如果您使用多个不同的账户或项目来管理成本，可以将它们的 Key 放在一个池子里，`alia_proxy` 会自动将请求和费用分散到这些账户中。

## 结合模型映射策略

API Key 轮换可以与[模型映射策略](./mapping.md)结合使用，创造出更复杂的路由逻辑。

例如，您可以创建两个都使用多 Key 轮换的 provider 实例，然后将它们放入一个模型映射池中：

```toml
# config.toml

[providers.openai-pool-A]
type = "openai"
api_key = ["sk-A1", "sk-A2"]

[providers.openai-pool-B]
type = "openai"
base_url = "https://api.example.com/v1" # 可能是另一个代理或区域
api_key = ["sk-B1", "sk-B2"]

[mapping]
# 对外暴露一个统一的 "production-gpt" 模型
# 流量会先在 A 和 B 两个池子间轮换
# 每个池子内部又会在各自的 Key 之间轮换
production-gpt = [
    "openai-pool-A/gpt-4o",
    "openai-pool-B/gpt-4o"
]
```

通过这种方式，您可以构建出一个高度可用和可扩展的 AI 请求处理架构。
