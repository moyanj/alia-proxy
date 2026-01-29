# PROVIDER STRATEGY

## OVERVIEW
Strategy Pattern implementation for mapping diverse AI APIs to a unified internal interface.

## WHERE TO LOOK
| Component | File | Role |
|-----------|------|------|
| **Base Interface** | `base.py` | `BaseProvider` abstract class & unified models (`ChatRequest`, `ChatResponse`) |
| **Factory** | `factory.py` | Provider registry & instantiation logic |
| **OpenAI Impl** | `openai.py` | Standard implementation (OpenAI, Ollama, DeepSeek) |
| **Anthropic Impl** | `anthropic.py` | Anthropic-specific message format translation |

## CONVENTIONS
- **Interface Adherence**: Must implement `chat`, `stream`, `image_gen`, `text_to_speech`.
- **Async First**: Use `httpx.AsyncClient` for all network I/O.
- **Unified Models**: Translate all upstream responses to `ChatResponse`/`Usage`.
- **Registry**: Register new providers in `ProviderFactory._registry`.

## ANTI-PATTERNS
- **Hardcoded Config**: Use `config.toml` injected params, not hardcoded URLs.
- **Sync SDKs**: Never use blocking SDKs (e.g. `requests`, official sync clients).
- **Leaky Abstractions**: Provider quirks must be handled internally, not exposed to routers.
