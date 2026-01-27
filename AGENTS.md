# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-27T14:00:22Z
**Commit:** 03b838d
**Branch:** main

## OVERVIEW
Unified AI API proxy built with FastAPI, supporting multiple providers (OpenAI, Anthropic, Ollama), with unified logging and media persistence.

## STRUCTURE
```
.
├── aiprox/               # Backend source code
│   ├── providers/        # Provider strategy implementations
│   ├── routers/          # API endpoints (OpenAI-compatible)
│   ├── services/         # Logger, Proxy, and Media services
│   ├── models.py         # Tortoise-ORM database models
│   ├── config.py         # Settings management (Pydantic)
│   └── main.py           # Application entry point
├── data/                 # Persistent storage (SQLite DB, Media)
├── tests/                # Pytest suite
├── config.toml           # Main provider configuration
└── pyproject.toml        # Dependency management (uv)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new AI Provider | `aiprox/providers/` | Implement `BaseProvider` & register in `factory.py` |
| Add new API Endpoint | `aiprox/routers/` | FastAPI routers (OpenAI compatible) |
| Database changes | `aiprox/models.py` | Tortoise-ORM Models |
| Configuration changes | `aiprox/config.py` | Pydantic Settings & `config.toml` |
| Business Logic | `aiprox/services/` | `proxy.py` orchestrates execution |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `ProxyService` | Class | `aiprox/services/proxy.py` | High-level orchestrator for AI requests |
| `BaseProvider` | Class | `aiprox/providers/base.py` | Abstract interface for all providers |
| `ProviderFactory` | Class | `aiprox/providers/factory.py` | Registry and instantiator for providers |
| `RequestLog` | Class | `aiprox/models.py` | Central database table for logs |
| `Settings` | Class | `aiprox/config.py` | Global configuration container |

## CONVENTIONS
- **Async-Only**: Use `async` for all route handlers and I/O. Use `httpx.AsyncClient`.
- **Dependency**: Managed via `uv`. Use `uv run` or `uv add`.
- **Testing**: Use `pytest` with in-memory SQLite isolation (`autouse` fixture).
- **Naming**: `aiprox/` is the core package (often referred to as `app` in generic docs).

## ANTI-PATTERNS (THIS PROJECT)
- **Hardcoded Keys**: NEVER put API keys in code. Use `config.toml`.
- **Sync DB calls**: DO NOT use synchronous ORMs or blocking drivers (e.g. `requests`).
- **Direct Provider Import**: Routers must use `ProxyService` or `ProviderFactory`.

## COMMANDS
```bash
# Run locally
uv run python -m aiprox.main

# Run tests
uv run pytest

# Docker
docker-compose up --build
```

## NOTES
- Media files (images/audio) are saved to `data/media/` and served via `/media/...`.
- Requests use `provider/model` format (e.g., `openai/gpt-4o`) in the `model` field.
