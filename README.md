# Agentic MCP Monorepo

A local-first monorepo that contains:

- **Modern chatbot UI** (React + Vite)
- **Agentic backend** (FastAPI + LangGraph) that can **plan**, **create tasks**, **execute** them, and summarize with an LLM
- **Sample FastMCP server** exposing tools for calculator + mock web search
- **Docker Compose** for one-command local startup

## Monorepo structure

```text
apps/
  backend/      # Agent API + planner/executor
  frontend/     # Chat interface + plan visualization
services/
  mcp-server/   # Sample FastMCP tool server (streamable HTTP)
```

## Environment variables (.env)

This repo reads runtime environment variables from a root `.env` file when running with Docker Compose.

1. Copy the example file:

```bash
cp .env.example .env
```

2. Edit `.env` values as needed.

A complete example is included in `.env.example`.

### Backend (`apps/backend`)

- `MCP_SERVER_URL` (default: `http://mcp-server:9000`)
  - URL for the MCP service that exposes tools.
- `CORS_ALLOWED_ORIGINS` (default: `http://localhost:5173,http://127.0.0.1:5173`)
  - Comma-separated list of browser origins allowed to call backend APIs directly.
- `OPENAI_API_KEY` (optional)
  - If set, backend uses OpenAI for final answer summarization.
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
  - Model used when `OPENAI_API_KEY` is set.

### Frontend (`apps/frontend`)

- `VITE_API_BASE` (recommended: `/api`)
  - Base URL used by browser fetch calls.
  - Use `/api` to keep requests same-origin via the Vite dev proxy and avoid CORS issues.
- `VITE_PROXY_TARGET` (default in Docker Compose: `http://backend:8000`)
  - Target for Vite's `/api` proxy.

## Run locally with Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- MCP server: http://localhost:9000

## Avoiding CORS issues in local UI development

By default, the frontend is configured to call `/api`, and Vite proxies `/api` to the backend.
That keeps browser traffic same-origin from `http://localhost:5173` and prevents CORS failures.

If you intentionally use a direct API URL (for example `VITE_API_BASE=http://localhost:8000`),
set backend `CORS_ALLOWED_ORIGINS` to include your frontend origin (for example
`http://localhost:5173`).

## Example prompt

Try in the UI:

> `research MCP workflow and calculate 12 + 30`

The backend will:

1. Build a plan.
2. Create tasks (internal + MCP tool calls).
3. Execute each task.
4. Return final summarized response and execution statuses.

## API endpoints

Backend:
- `GET /health`
- `GET /mcp/tools`
- `POST /chat`

MCP server:
- `GET /health`
- `GET /mcp/tools`
- `POST /mcp/tools/{tool_name}/invoke`
