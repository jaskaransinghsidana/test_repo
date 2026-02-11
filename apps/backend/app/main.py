from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from .agent import AgentOrchestrator
from .models import ChatRequest, ChatResponse, MCPTool

app = FastAPI(title="Agentic Chat Backend", version="0.1.0")
agent = AgentOrchestrator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/mcp/tools")
async def mcp_tools() -> dict[str, list[MCPTool]]:
    tools = await agent.mcp_client.list_tools()
    return {"tools": tools}


@app.get("/mcp/examples")
async def mcp_examples() -> dict[str, list[dict[str, Any]]]:
    examples = await agent.mcp_client.list_examples()
    return {"examples": examples}


@app.get("/chat")
async def chat_usage() -> dict[str, str]:
    return {
        "detail": "Use POST /chat with JSON body {'message': '...'} to execute an agent run."
    }


@app.post("/chat", response_model=ChatResponse)
@app.post("/chat/", response_model=ChatResponse, include_in_schema=False)
async def chat(request: ChatRequest) -> ChatResponse:
    plan = await agent.plan(request.message)
    executed_plan = await agent.execute(plan)

    final_task = next(
        (task for task in reversed(executed_plan.tasks) if task.title == "Summarize and respond"),
        executed_plan.tasks[-1],
    )

    return ChatResponse(reply=str(final_task.result), plan=executed_plan)


@app.options("/chat", include_in_schema=False)
@app.options("/chat/", include_in_schema=False)
async def chat_preflight() -> Response:
    return Response(status_code=204)
