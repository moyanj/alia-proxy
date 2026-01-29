# AI PROXY BACKEND CORE

## OVERVIEW
FastAPI-based unified AI proxy handler. Manages multi-provider routing, unified logging to SQLite, and media persistence.

## STRUCTURE
```
aiprox/
├── providers/        # Provider strategy implementations
├── routers/          # API endpoints (OpenAI-compatible)
├── services/         # Core business logic (Logger, Proxy, Media)
├── models.py         # Tortoise-ORM schema
├── config.py         # Pydantic Settings
└── main.py           # Entry point & lifespan management
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| **App Entry** | `main.py` | FastAPI app creation, middleware, router mounting |
| **Config** | `config.py` | Loads settings from `config.toml` |
| **Database** | `models.py` | Defines `RequestLog` and other tables |
| **Dependencies** | `routers/deps.py` | Dependency injection (e.g. `get_proxy_service`) |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `create_app` | Function | `main.py` | App factory |
| `Settings` | Class | `config.py` | Configuration singleton |
| `RequestLog` | Class | `models.py` | Main log entity |

## CONVENTIONS
- **Provider Abstraction**: Routers never import concrete providers. Use `ProxyService`.
- **Schema Validation**: All internal data uses Pydantic `BaseModel`.
- **Telegraphic Style**: Keep documentation focused on "where" and "how".

## ANTI-PATTERNS
- **Sync DB Access**: `models.py` usage must be async.
- **Global State**: Avoid global variables; use `config.py` or Dependency Injection.
