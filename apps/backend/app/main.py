from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent import AgentOrchestrator

app = FastAPI(title="Agentic Chat Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
agent = AgentOrchestrator()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/mcp/tools")
async def mcp_tools() -> dict[str, list[dict]]:
    tools = await agent.mcp_client.list_tools()
    return {"tools": [tool.to_dict() for tool in tools]}


@app.get("/chat")
async def chat_usage() -> dict[str, str]:
    return {"detail": "Use POST /chat with JSON body: {'message': '...'}"}


@app.post("/chat")
async def chat(request: dict[str, str]) -> dict[str, object]:
    message = request.get("message", "").strip()
    if not message:
        return {"reply": "Please provide a message.", "plan": {"goal": "", "tasks": []}}

    reply, executed_plan = await agent.run(message)
    return {"reply": reply, "plan": executed_plan.to_dict()}
