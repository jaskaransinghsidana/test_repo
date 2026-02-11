from __future__ import annotations

from fastapi import FastAPI

from .agent import AgentOrchestrator
from .models import ChatRequest, ChatResponse, MCPTool

app = FastAPI(title="Agentic Chat Backend", version="0.1.0")
agent = AgentOrchestrator()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/mcp/tools")
async def mcp_tools() -> dict[str, list[MCPTool]]:
    tools = await agent.mcp_client.list_tools()
    return {"tools": tools}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    plan = await agent.plan(request.message)
    executed_plan = await agent.execute(plan)

    final_task = next(
        (task for task in reversed(executed_plan.tasks) if task.title == "Summarize and respond"),
        executed_plan.tasks[-1],
    )

    return ChatResponse(reply=str(final_task.result), plan=executed_plan)
