from __future__ import annotations

import pytest

from app.agent import AgentOrchestrator
from app.models import MCPTool


class FakeMCP:
    async def list_tools(self):
        return [
            MCPTool(name="calculator", description="math"),
            MCPTool(name="web_search", description="search"),
        ]

    async def call_tool(self, name, arguments):
        if name == "calculator":
            return arguments["a"] + arguments["b"]
        if name == "web_search":
            return f"results for {arguments['query']}"
        return "noop"


@pytest.mark.asyncio
async def test_plan_and_execute_uses_tools():
    agent = AgentOrchestrator(mcp_client=FakeMCP())
    plan = await agent.plan("research MCP and calculate 2 + 3")
    executed = await agent.execute(plan)

    calc_task = next(task for task in executed.tasks if task.tool_name == "calculator")
    assert calc_task.result == 5
    assert "Research findings" in str(executed.tasks[-1].result)
