# 新增 Provider

想要支持一个新的 AI 服务商？只需按照以下步骤实现一个新的 Provider 类。

## 1. 继承 BaseProvider

在 `aiprox/providers/` 目录下创建一个新文件（例如 `myprovider.py`）。继承 `BaseProvider` 类并实现必要的抽象方法。

```python
from .base import BaseProvider, ChatRequest, ChatResponse, ProviderConfig
from typing import AsyncGenerator, Dict, Any

class MyNewProvider(BaseProvider):
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        # 初始化 HTTP 客户端或其他资源
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        # 1. 将通用 request 转换为 MyProvider 所需的 payload
        # 2. 发送 HTTP 请求
        # 3. 将响应转换为通用的 ChatResponse
        pass

    async def stream(self, request: ChatRequest) -> AsyncGenerator[Dict[str, Any], None]:
        # 1. 发起流式请求
        # 2. 逐行解析响应
        # 3. yield 符合 OpenAI 格式的 chunk
        pass
```

## 2. 注册 Provider

打开 `aiprox/providers/factory.py`，在 `ProviderFactory` 类中注册您的新类。

```python
from .myprovider import MyNewProvider

class ProviderFactory:
    # ...
    
    def _create_provider(self, config: ProviderConfig) -> BaseProvider:
        if config.type == "openai":
            return OpenAIProvider(config)
        elif config.type == "anthropic":
            return AnthropicProvider(config)
        elif config.type == "my-new-type":  # 添加这一行
            return MyNewProvider(config)
        # ...
```

## 3. 配置与使用

现在，您可以在 `config.toml` 中使用新的类型了：

```toml
[providers.my-custom-service]
type = "my-new-type"
api_key = "..."
```

然后发送请求：

```bash
curl ... -d '{"model": "my-custom-service/some-model", ...}'
```

## 最佳实践

- **异常处理**: 捕获上游 API 的错误（如 401, 429），并抛出 `HTTPException`，以便 Router 层能返回正确的状态码给客户端。
- **配置灵活性**: 尽量使用 `self.config` 中的参数（如 `base_url`, `timeout`），而不是硬编码 URL。
- **流式适配**: 如果上游的流式协议很特殊（如 SSE 事件名不同），请参考 `AnthropicProvider` 中的实现，编写一个适配器将其转换为 OpenAI 标准的 delta 格式。
