from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(slots=True)
class ToolInfo:
    name: str
    description: str
    inputSchema: dict[str, Any]


@dataclass(slots=True)
class ToolResult:
    data: Any


class Client:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.aclose()
        self._client = None

    async def list_tools(self) -> list[ToolInfo]:
        assert self._client is not None
        response = await self._client.get(f"{self.base_url}/tools")
        response.raise_for_status()
        payload = response.json()
        return [
            ToolInfo(
                name=tool.get("name", "unknown"),
                description=tool.get("description", ""),
                inputSchema=tool.get("inputSchema", {}),
            )
            for tool in payload.get("tools", [])
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        assert self._client is not None
        response = await self._client.post(
            f"{self.base_url}/tools/{name}/invoke",
            json={"arguments": arguments},
        )
        response.raise_for_status()
        payload = response.json()
        return ToolResult(data=payload.get("result"))
