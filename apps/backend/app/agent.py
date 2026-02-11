from __future__ import annotations

import os
import re
from typing import Any

from .mcp_client import MCPClient
from .models import AgentPlan, PlannedTask, TaskStatus


class AgentOrchestrator:
    def __init__(self, mcp_client: MCPClient | None = None) -> None:
        server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:9000")
        self.mcp_client = mcp_client or MCPClient(server_url)

    async def plan(self, user_message: str) -> AgentPlan:
        available_tools = await self.mcp_client.list_tools()
        tool_names = {tool.name for tool in available_tools}

        tasks: list[PlannedTask] = [
            PlannedTask(
                id=1,
                title="Understand user objective",
                description=f"Parse request: {user_message}",
            )
        ]

        if "research" in user_message.lower() and "web_search" in tool_names:
            query = user_message.replace("research", "").strip() or user_message
            tasks.append(
                PlannedTask(
                    id=2,
                    title="Research via MCP tool",
                    description="Use web_search to gather context.",
                    tool_name="web_search",
                    tool_input={"query": query},
                )
            )

        math_match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", user_message)
        if math_match and "calculator" in tool_names:
            a, op, b = math_match.groups()
            tasks.append(
                PlannedTask(
                    id=len(tasks) + 1,
                    title="Compute expression",
                    description="Use calculator MCP tool for arithmetic.",
                    tool_name="calculator",
                    tool_input={"a": float(a), "b": float(b), "operator": op},
                )
            )

        tasks.append(
            PlannedTask(
                id=len(tasks) + 1,
                title="Summarize and respond",
                description="Combine outcomes into a concise assistant answer.",
            )
        )

        return AgentPlan(goal=user_message, tasks=tasks)

    async def execute(self, plan: AgentPlan) -> AgentPlan:
        memory: dict[str, Any] = {}
        for task in plan.tasks:
            task.status = TaskStatus.RUNNING
            if task.tool_name:
                try:
                    result = await self.mcp_client.call_tool(task.tool_name, task.tool_input)
                    task.result = result
                    memory[task.tool_name] = result
                    task.status = TaskStatus.COMPLETED
                except Exception as exc:  # noqa: BLE001
                    task.result = {"error": str(exc)}
                    task.status = TaskStatus.FAILED
            else:
                task.result = self._run_internal_task(task, memory)
                task.status = TaskStatus.COMPLETED
        return plan

    @staticmethod
    def _run_internal_task(task: PlannedTask, memory: dict[str, Any]) -> Any:
        if task.title == "Summarize and respond":
            snippets = []
            if "web_search" in memory:
                snippets.append(f"Research findings: {memory['web_search']}")
            if "calculator" in memory:
                snippets.append(f"Math result: {memory['calculator']}")
            if not snippets:
                snippets.append("No external tools were required. I created a plan and executed it.")
            return " | ".join(snippets)
        return f"Completed: {task.description}"
