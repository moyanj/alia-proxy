# PROVIDER STRATEGY

## OVERVIEW
Unified Strategy Pattern implementation for mapping diverse AI backend APIs to a consistent internal interface.

## WHERE TO LOOK
- `base.py`: The foundation of the provider system. It defines the `BaseProvider` abstract base class and the unified Pydantic models (`ChatRequest`, `ChatResponse`, `Usage`) used across the entire application.
- `factory.py`: The central hub for provider management. It handles the mapping between provider types (e.g., "openai") and their implementations, manages instance caching, and resolves `provider/model` strings.
- `openai.py`: The most versatile implementation. It handles standard OpenAI API calls and is also used for compatible backends like Ollama, DeepSeek, and other local or third-party LLM providers.
- `anthropic.py`: A specialized implementation for Anthropic's Messages API. It handles the translation of unified messages into Anthropic's specific format and vice versa.

## CONVENTIONS
- **Strict Interface Adherence**: Every provider must implement the full suite of methods defined in `BaseProvider`, including `chat`, `stream`, `image_gen`, and `text_to_speech`, even if only to raise `NotImplementedError`.
- **Asynchronous First**: All network I/O must be performed using `httpx.AsyncClient`. Synchronous calls are strictly forbidden as they block the FastAPI event loop and degrade performance.
- **Unified Response Mapping**: Providers are responsible for translating upstream API responses into the standard `ChatResponse` and `Usage` models defined in `base.py`.
- **Streaming Format Consistency**: When implementing `stream`, providers must yield dictionaries that conform to the OpenAI-compatible streaming chunk format to ensure frontend compatibility.
- **Registry-Based Extension**: To add a new provider type, implement the class and register it in `ProviderFactory._registry`. This allows the `ProxyService` to resolve it dynamically.

## ANTI-PATTERNS
- **Configuration Hardcoding**: Avoid embedding provider-specific defaults (like base URLs or model names) in the code; these should be driven by the `config.toml` parameters passed during initialization.
- **Synchronous Library Dependencies**: Avoid using libraries like `requests` or the synchronous versions of provider SDKs. Always prefer `httpx` or async-native SDKs to prevent event loop starvation.
- **Leaky Provider Logic**: Provider-specific quirks, such as unique error codes or payload structures, must be encapsulated within the provider class and never exposed to the routers.
- **Manual Instance Management**: Do not attempt to manage provider lifecycles or caching manually; the `ProviderFactory` is the sole authority for creating and retrieving provider instances.
- **Inconsistent Token Counting**: Ensure that token usage is correctly extracted and mapped to the `Usage` model, as this data is critical for the application's logging and analytics features.
