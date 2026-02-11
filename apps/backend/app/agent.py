from __future__ import annotations

import os
import re
from typing import Any, TypedDict

import httpx
from langgraph.graph import END, START, StateGraph

from .mcp_client import MCPClient
from .models import AgentPlan, PlannedTask, TaskStatus


class AgentState(TypedDict):
    user_message: str
    available_tools: list[str]
    plan: AgentPlan
    memory: dict[str, Any]
    reply: str


class AgentOrchestrator:
    def __init__(self, mcp_client: MCPClient | None = None) -> None:
        server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:9000")
        self.mcp_client = mcp_client or MCPClient(server_url)
        self._graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("discover_tools", self._discover_tools)
        workflow.add_node("build_plan", self._build_plan)
        workflow.add_node("execute_tasks", self._execute_tasks)
        workflow.add_node("summarize", self._summarize)

        workflow.add_edge(START, "discover_tools")
        workflow.add_edge("discover_tools", "build_plan")
        workflow.add_edge("build_plan", "execute_tasks")
        workflow.add_edge("execute_tasks", "summarize")
        workflow.add_edge("summarize", END)
        return workflow.compile()

    async def run(self, user_message: str) -> tuple[str, AgentPlan]:
        initial_plan = AgentPlan(goal=user_message, tasks=[])
        result = await self._graph.ainvoke(
            {
                "user_message": user_message,
                "available_tools": [],
                "plan": initial_plan,
                "memory": {},
                "reply": "",
            }
        )
        return result["reply"], result["plan"]

    async def _discover_tools(self, state: AgentState) -> AgentState:
        tools = await self.mcp_client.list_tools()
        state["available_tools"] = [tool.name for tool in tools]
        return state

    def _build_plan(self, state: AgentState) -> AgentState:
        user_message = state["user_message"]
        tool_names = set(state["available_tools"])

        tasks: list[PlannedTask] = [
            PlannedTask(id=1, title="Understand user objective", description=f"Parse request: {user_message}")
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
        state["plan"] = AgentPlan(goal=user_message, tasks=tasks)
        return state

    async def _execute_tasks(self, state: AgentState) -> AgentState:
        memory: dict[str, Any] = {}
        for task in state["plan"].tasks:
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
                task.result = f"Completed: {task.description}"
                task.status = TaskStatus.COMPLETED

        state["memory"] = memory
        return state

    async def _summarize(self, state: AgentState) -> AgentState:
        memory = state["memory"]
        snippets: list[str] = []
        if "web_search" in memory:
            snippets.append(f"Research findings: {memory['web_search']}")
        if "calculator" in memory:
            snippets.append(f"Math result: {memory['calculator']}")
        if not snippets:
            snippets.append("No external tools were required. I created a plan and executed it.")

        state["reply"] = await self._summarize_with_llm(state["user_message"], snippets)

        for task in reversed(state["plan"].tasks):
            if task.title == "Summarize and respond":
                task.result = state["reply"]
                task.status = TaskStatus.COMPLETED
                break
        return state

    async def _summarize_with_llm(self, user_message: str, snippets: list[str]) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return " | ".join(snippets)

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = (
            "You are an assistant summarizing tool outputs for a chat reply. "
            f"User asked: {user_message}\n"
            f"Tool outputs: {snippets}\n"
            "Give a concise, helpful answer."
        )

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )

        if response.status_code >= 400:
            return " | ".join(snippets)

        payload = response.json()
        choices = payload.get("choices", [])
        if not choices:
            return " | ".join(snippets)

        message = choices[0].get("message", {})
        return str(message.get("content", " | ".join(snippets)))
