from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP

mcp = FastMCP(name="sample-mcp-server")


@mcp.tool(
    name="calculator",
    description="Execute basic arithmetic operations.",
)
def calculator(a: float, b: float, operator: Literal['+', '-', '*', '/']) -> float | str:
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        return a / b if b != 0 else "division by zero"
    return "unsupported operator"


@mcp.tool(
    name="web_search",
    description="Return mocked search snippets for a query.",
)
def web_search(query: str) -> list[str]:
    return [
        f"Top hit for '{query}'",
        "MCP lets agents discover and invoke tools through a standard protocol.",
        "Use planner + executor loops for robust agentic workflows.",
    ]


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000, path="/mcp")
