from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sample MCP Server", version="0.1.0")


class ToolRequest(BaseModel):
    arguments: dict


TOOLS = [
    {
        "name": "calculator",
        "description": "Execute basic arithmetic operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "operator": {"type": "string", "enum": ["+", "-", "*", "/"]},
            },
            "required": ["a", "b", "operator"],
        },
    },
    {
        "name": "web_search",
        "description": "Return mocked search snippets for a query.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

EXAMPLES = [
    {
        "title": "Calculator example",
        "goal": "Compute a simple expression",
        "tool_name": "calculator",
        "arguments": {"a": 12, "b": 30, "operator": "+"},
        "expected_result": 42,
        "chat_prompt": "calculate 12 + 30",
    },
    {
        "title": "Research example",
        "goal": "Fetch MCP context snippets",
        "tool_name": "web_search",
        "arguments": {"query": "MCP workflow for agent planning"},
        "expected_result": "list of mocked snippets",
        "chat_prompt": "research MCP workflow for agent planning",
    },
    {
        "title": "Combined agentic run",
        "goal": "Use both tools inside one plan",
        "tool_name": "multi_step",
        "arguments": {"prompt": "research MCP workflow and calculate 12 + 30"},
        "expected_result": "research snippets + math result in assistant summary",
        "chat_prompt": "research MCP workflow and calculate 12 + 30",
    },
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tools")
def list_tools() -> dict[str, list[dict]]:
    return {"tools": TOOLS}


@app.get("/examples")
def list_examples() -> dict[str, list[dict]]:
    return {"examples": EXAMPLES}


@app.post("/tools/{tool_name}/invoke")
def invoke_tool(tool_name: str, req: ToolRequest) -> dict:
    args = req.arguments

    if tool_name == "calculator":
        a, b, op = float(args["a"]), float(args["b"]), args["operator"]
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            result = a / b if b != 0 else "division by zero"
        else:
            raise HTTPException(status_code=400, detail="Unsupported operator")
        return {"result": result}

    if tool_name == "web_search":
        query = str(args.get("query", ""))
        return {
            "result": [
                f"Top hit for '{query}'",
                "MCP lets agents discover and invoke tools through a standard protocol.",
                "Use planner + executor loops for robust agentic workflows.",
            ]
        }

    raise HTTPException(status_code=404, detail="Unknown tool")
