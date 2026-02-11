from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    inputSchema: dict[str, Any]


class _InvokePayload(BaseModel):
    arguments: dict[str, Any]


class FastMCP:
    def __init__(self, name: str) -> None:
        self.name = name
        self._tools: dict[str, tuple[Callable[..., Any], ToolSpec]] = {}

    def tool(self, name: str, description: str):
        def _decorator(func: Callable[..., Any]):
            signature = inspect.signature(func)
            properties = {}
            required = []
            for param in signature.parameters.values():
                required.append(param.name)
                properties[param.name] = {"type": "string"}
            schema = {"type": "object", "properties": properties, "required": required}
            self._tools[name] = (func, ToolSpec(name=name, description=description, inputSchema=schema))
            return func

        return _decorator

    def _create_app(self, path: str) -> FastAPI:
        app = FastAPI(title=self.name)

        @app.get("/health")
        def _health() -> dict[str, str]:
            return {"status": "ok"}

        @app.get(f"{path}/tools")
        def _tools() -> dict[str, list[dict[str, Any]]]:
            return {"tools": [spec.__dict__ for _, spec in self._tools.values()]}

        @app.post(f"{path}/tools/{{tool_name}}/invoke")
        def _invoke(tool_name: str, payload: _InvokePayload) -> dict[str, Any]:
            tool = self._tools.get(tool_name)
            if not tool:
                raise HTTPException(status_code=404, detail="Unknown tool")
            func, _ = tool
            return {"result": func(**payload.arguments)}

        return app

    def run(self, transport: str, host: str, port: int, path: str = "/mcp") -> None:
        if transport != "streamable-http":
            raise ValueError("Only streamable-http transport is supported in this implementation")
        app = self._create_app(path)
        uvicorn.run(app, host=host, port=port)
