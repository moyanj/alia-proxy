# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-29T13:15:00Z
**Commit:** current
**Branch:** main

## OVERVIEW
Unified AI API proxy built with FastAPI, supporting multiple providers (OpenAI, Anthropic, Ollama), with unified logging, media persistence, and a Vue.js web dashboard.

## STRUCTURE
```
.
├── aiprox/               # Backend source code (FastAPI)
│   ├── providers/        # AI Provider implementations (OpenAI, Anthropic)
│   ├── routers/          # API endpoints (OpenAI-compatible)
│   ├── services/         # Core business logic (Proxy, Logger, Media)
│   ├── models.py         # Tortoise-ORM database models
│   └── main.py           # Application entry point
├── frontend/             # Vue.js Web Dashboard
│   ├── src/views/        # Page views (Dashboard, Logs, Playground)
│   └── src/stores/       # State management (Pinia)
├── data/                 # Persistent storage (SQLite DB, Media)
├── tests/                # Pytest suite
├── config.toml           # Main provider configuration
└── pyproject.toml        # Dependency management (uv)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| **Add AI Provider** | `aiprox/providers/` | Implement `BaseProvider` & register in `factory.py` |
| **Add API Endpoint** | `aiprox/routers/` | FastAPI routers (OpenAI compatible) |
| **Frontend Page** | `frontend/src/views/` | Vue.js views |
| **Database Schema** | `aiprox/models.py` | Tortoise-ORM Models |
| **Configuration** | `aiprox/config.py` | Pydantic Settings & `config.toml` |
| **Business Logic** | `aiprox/services/` | `proxy.py` orchestrates execution |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `ProxyService` | Class | `aiprox/services/proxy.py` | High-level orchestrator for AI requests |
| `BaseProvider` | Class | `aiprox/providers/base.py` | Abstract interface for all providers |
| `ProviderFactory` | Class | `aiprox/providers/factory.py` | Registry and instantiator for providers |
| `RequestLog` | Class | `aiprox/models.py` | Central database table for logs |
| `Settings` | Class | `aiprox/config.py` | Global configuration container |

## CONVENTIONS
- **Async-Only**: Use `async` for all backend route handlers and I/O.
- **Dependency**: Python: `uv`; Frontend: `pnpm`.
- **Testing**: `pytest` with in-memory SQLite isolation.
- **Naming**: `aiprox/` is the core backend package.

## ANTI-PATTERNS (THIS PROJECT)
- **Hardcoded Keys**: NEVER put API keys in code. Use `config.toml`.
- **Sync DB calls**: DO NOT use synchronous ORMs or blocking drivers.
- **Direct Provider Import**: Routers must use `ProxyService` or `ProviderFactory`.

## COMMANDS
```bash
# Backend
uv run python -m aiprox.main
uv run pytest

# Frontend
cd frontend && pnpm dev
cd frontend && pnpm build

# Docker
docker-compose up --build
```

## NOTES
- Media files (images/audio) are saved to `data/media/` and served via `/api/media/...`.
- Requests use `provider/model` format (e.g., `openai/gpt-4o`) in the `model` field.
