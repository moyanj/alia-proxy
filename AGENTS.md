# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-26
**Project:** AI Proxy Service (aiprox)

## OVERVIEW
Unified AI API proxy built with FastAPI, supporting multiple providers (OpenAI, Anthropic, Ollama), and logging to SQLite.

## STRUCTURE
```
.
├── app/                  # Backend source code
│   ├── providers/        # Provider strategy implementations
│   ├── routers/          # API endpoints (OpenAI-compatible)
│   ├── services/         # Logger and Media services
│   ├── models.py         # Tortoise-ORM database models
│   └── config.py         # Settings management (Pydantic)
├── data/                 # Persistent storage (SQLite DB, Media)
├── config.toml           # Main provider configuration
└── pyproject.toml        # Dependency management (uv)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new AI Provider | `app/providers/` | Implement `BaseProvider` |
| Add new API Endpoint | `app/routers/` | FastAPI routers |
| Database changes | `app/models.py` | Tortoise Models |
| Configuration changes | `app/config.py` | Pydantic Settings |

## CONVENTIONS
- **FastAPI**: Use `async` for all route handlers.
- **Dependency**: Managed via `uv`. Use `uv add` for new packages.
- **Settings**: All configurations should be defined in `app/config.py` and loaded from `config.toml`.
- **Database**: Use Tortoise-ORM for models and SQLite (aiosqlite) for storage.

## ANTI-PATTERNS (THIS PROJECT)
- **Hardcoded Keys**: NEVER put API keys in code. Use `config.toml`.
- **Sync DB calls**: DO NOT use synchronous ORMs or blocking drivers.

## COMMANDS
```bash
# Run locally
uv run python -m app.main

# Run with Docker
docker-compose up --build
```

## NOTES
- Media files are saved to `data/media/` and served via authenticated routes.
