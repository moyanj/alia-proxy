# PROVIDER STRATEGY

## OVERVIEW
Implements the Strategy Pattern to unify diverse AI provider APIs (OpenAI, Anthropic, etc.) into a single internal interface.

## CORE COMPONENTS
- **BaseProvider (`base.py`)**: Abstract base class defining the unified interface.
- **ProviderFactory (`factory.py`)**: Handles instantiation and caching of provider instances using a Registry pattern.
- **Implementations**:
  - `OpenAIProvider`: Handles OpenAI and compatible APIs.
  - `AnthropicProvider`: Maps Anthropic's Messages API.

## HOW TO ADD A NEW PROVIDER
1. **Implement Strategy**:
   - Create `app/providers/your_provider.py` inheriting from `BaseProvider`.
2. **Register in Factory**:
   - Add it to the `_registry` in `factory.py` or use `ProviderFactory.register`.
3. **Configure**:
   - Add to `config.toml` with `type = "your_type"`.

## CONVENTIONS
- **Async First**: Use `httpx.AsyncClient` for all network operations.
- **Unified Models**: Always return `ChatResponse` or `Usage` objects from `base.py`.
- **Error Handling**: Raise `httpx.HTTPStatusError` for API failures to be caught by routers.

## ANTI-PATTERNS
- **Hardcoded Keys**: Never store API keys in provider files; use `self.api_key`.
- **Sync Calls**: Avoid `requests` or other blocking libraries.
- **Direct Router Logic**: Keep provider-specific mapping logic inside the provider class.
