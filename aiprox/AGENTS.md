# APP INTERNALS KNOWLEDGE BASE

## OVERVIEW
FastAPI backend implementing a provider-agnostic AI proxy. Handles dynamic routing, multimedia persistence, and unified logging.

## CORE MODULES
- **main.py**: Application entry point.
  - Initializes SQLite DB via `lifespan` context manager.
  - Mounts routers: `openai`, `media`, `export`, `common`.
- **config.py**: Settings management.
  - Loads `config.toml` into Pydantic `Settings`.
  - Supports environment overrides via `AIPROX_` prefix.
- **models.py**: Data layer.
  - Uses `SQLModel` for ORM.
  - `RequestLog`: Primary table for tracking all proxy activity.

## ROUTING & LOGIC
- **routers/openai.py**: API endpoints.
  - Uses `get_proxy_service` dependency to resolve providers.
- **routers/deps.py**: FastAPI dependencies.
  - Handles parsing `provider/model` and instantiating `ProxyService`.
- **services/proxy.py**: The "Brain" of the proxy.
  - Orchestrates calls between `providers` and `services` (logger, media).
  - Handles streaming responses and media persistence.
- **providers/**: Strategy pattern for AI backends.

## DATA FLOW
1. **Request** arrives at `routers/openai.py`.
2. **Dependency** `get_proxy_service` resolves provider via `ProviderFactory` and returns `ProxyService`.
3. **Router** calls `ProxyService` methods.
4. **ProxyService** calls **Provider** to execute API call to upstream.
5. **ProxyService** processes response, calls `services.media` and `services.logger`.
6. **Response** returned to client.


## CONVENTIONS
- **Async First**: All I/O bound operations (API calls, DB, File) must be `async`.
- **Provider Agnostic**: Routers should interact with `BaseProvider` interface, not concrete classes.
