# AI Proxy Service (aiprox)

Unified AI API proxy supporting multiple providers, logging, and WebUI stats.

## Features

- **Multi-Provider Support**: OpenAI, Anthropic, Ollama, and other OpenAI-compatible APIs.
- **Dynamic Routing**: Route requests using the `provider/model` format (e.g., `gpt4-main/gpt-4o`).
- **High Availability**: Automatic fallback to backup models/providers when the primary fails.
- **Multimedia Support**: Image Generation (`/v1/images/generations`) and Text-to-Speech (`/v1/audio/speech`).
- **Local Media Storage**: Media files are saved to `data/media/` and served via authenticated API.
- **Unified Logging**: All requests and responses (including media paths) are logged to a SQLite database.
- **Export System**: Export logs as ShareGPT JSONL or CSV.
- **Web Dashboard**: View real-time stats, logs, and multimedia outputs.

## Project Structure

```
/
├── app/                  # Backend FastAPI application
│   ├── providers/        # Provider strategy implementations
│   ├── routers/          # API endpoints
│   ├── services/         # Core business logic (logging, media)
│   ├── models.py         # Database models
│   └── config.py         # Configuration loader
├── frontend/             # Vue.js Dashboard
├── data/                 # Persistent storage (SQLite DB, Media)
├── config.toml           # Provider configuration
└── docker-compose.yml    # Container orchestration
```

## Quick Start

1. **Configure Providers**: Edit `config.toml` to add your API keys.
2. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```
3. **Access Dashboard**: Open `http://localhost:3000` in your browser.

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
