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

## Run locally with Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- MCP server: http://localhost:9000


### Avoiding CORS issues in local UI development

The frontend uses a Vite proxy by default (`/api -> http://backend:8000`) so browser requests are same-origin from `http://localhost:5173` and do not require CORS preflight handling in the browser path.

If you override `VITE_API_BASE`, use a same-origin value when possible (for example `/api`) to avoid preflight/CORS errors in development.

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
