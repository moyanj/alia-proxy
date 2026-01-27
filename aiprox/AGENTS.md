# AI PROXY CORE

## OVERVIEW
FastAPI-based unified AI proxy handler. Manages multi-provider routing, unified logging to SQLite, and media persistence.

## CORE MODULES
- **main.py**: Entry point. Manages lifespan (ORM init) and mounts routers.
- **config.py**: Pydantic `Settings`. Loads `config.toml` and env `AIPROX_*`.
- **models.py**: Tortoise-ORM schema. `RequestLog` stores prompts, usage, and media refs.
- **services/proxy.py**: Orchestrator. Resolves providers via factory and manages logging/media logic.
- **routers/deps.py**: FastAPI dependencies. `get_proxy_service` parses `provider/model`.

## DATA FLOW
1. **Request**: Client sends OpenAI-compatible JSON to `/v1/...`.
2. **Dependency**: `get_proxy_service` resolves provider ID from `model` field.
3. **Execution**: `ProxyService` calls provider, logs results, and saves media via `MediaService`.
4. **Response**: Streamed or buffered response returned to client.

## CONVENTIONS
- **Provider Abstraction**: Routers never import concrete providers.
- **Schema Validation**: All internal data uses Pydantic `BaseModel`.
- **Telegraphic Style**: Keep documentation focused on "where" and "how".
