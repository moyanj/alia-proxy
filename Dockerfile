# Frontend build stage
FROM node:22-slim AS frontend-builder

WORKDIR /app/frontend

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy frontend files
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
COPY frontend/tsconfig*.json ./
COPY frontend/vite.config.ts ./
COPY frontend/index.html ./
COPY frontend/src/ ./src/
COPY frontend/public/ ./public/

# Install dependencies and build
RUN pnpm install --frozen-lockfile || pnpm install
RUN pnpm build-only

# Backend dependencies stage
FROM python:3.12-slim AS backend-builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from backend builder
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application code
COPY alia_proxy/ ./alia_proxy/
COPY config.toml ./

# Copy built frontend from frontend builder
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create data directory for SQLite and media storage
RUN mkdir -p data/media

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "alia_proxy.main"]
