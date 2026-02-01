# AI Proxy Service (aiprox)

<p align="center">
  <a href="https://github.com/moyanj/aiprox/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://github.com/moyanj/aiprox/actions"><img src="https://img.shields.io/github/actions/workflow/status/moyanj/aiprox/docs.yml?label=docs" alt="Docs CI"></a>
  <img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/node-20+-green.svg" alt="Node 20+">
  <a href="https://moyanj.github.io/aiprox/"><img src="https://img.shields.io/badge/docs-online-blue.svg" alt="Documentation"></a>
</p>

<p align="center">
  Unified AI API proxy supporting multiple providers, logging, WebUI stats and multi-database.
</p>

<p align="center">
  English | <a href="./README.md">简体中文</a>
</p>

## Features

- **Multi-Provider Support**: OpenAI, Anthropic, Ollama, and other OpenAI-compatible APIs.
- **Dynamic Routing**: Route requests using the `provider/model` format (e.g., `gpt4-main/gpt-4o`).
- **High Availability**: Automatic fallback to backup models/providers when the primary fails.
- **Multimedia Support**: Image Generation (`/v1/images/generations`) and Text-to-Speech (`/v1/audio/speech`).
- **Local Media Storage**: Media files are saved to `data/media/` and served via authenticated API.
- **Unified Logging**: All requests and responses (including media paths) are logged to database.
- **Export System**: Export logs as ShareGPT JSONL or CSV.
- **Web Dashboard**: View real-time stats, logs, and multimedia outputs.
- **Multi-Database Support**: SQLite (default), PostgreSQL, MySQL.

## Project Structure

```
/
├── aiprox/               # Backend FastAPI application
│   ├── providers/        # Provider strategy implementations
│   ├── routers/          # API endpoints
│   ├── services/         # Core business logic (logging, media)
│   ├── models.py         # Database models
│   └── main.py           # Application entry point
├── frontend/             # Vue.js Dashboard
├── data/                 # Persistent storage (SQLite DB, Media)
├── config.toml           # Provider configuration
├── docker-compose.yml    # Container orchestration
├── Dockerfile            # Single Dockerfile for frontend + backend
└── docs/                 # mdBook documentation
```

## Quick Start

### Using Docker (Recommended)

The easiest way to get started. Both frontend and backend are built into a single container.

1. **Configure Providers**:
   ```bash
   cp config.example.toml config.toml
   # Edit config.toml to add your API keys
   ```

2. **Configure Environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to customize database, debug mode, etc.
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Access Application**:
   - **Web Dashboard**: http://localhost:8000
   - **API Service**: http://localhost:8000/v1/...

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AIPROX_DATABASE_URL` | `sqlite:///data/aiprox.db` | Database connection string (supports SQLite, PostgreSQL, MySQL) |
| `AIPROX_MEDIA_DIR` | `/home/moyan/projects/aiprox/data/media` | Media file storage directory |
| `AIPROX_DEBUG` | `false` | Enable debug mode |
| `AIPROX_HOT_RELOAD` | `false` | Enable config.toml hot reload |

### Using PostgreSQL instead of SQLite

1. Edit `.env`:
   ```bash
   AIPROX_DATABASE_URL=postgres://user:password@host:5432/aiprox
   ```

2. Uncomment the PostgreSQL service in `docker-compose.yml`

## Manual Installation (Development)

### Backend

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml

# Run
cp config.example.toml config.toml
uv run python -m aiprox.main
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## API Usage

Example Chat Completion:
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt4-main/gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Documentation

- [Online Documentation](https://moyanj.github.io/aiprox/)
- [中文文档](./README.md)
- Full documentation is available in the `docs/` directory.

## License

MIT License
