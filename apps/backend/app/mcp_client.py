from __future__ import annotations

from typing import Any

import httpx

from .models import MCPTool


class MCPClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def list_tools(self) -> list[MCPTool]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/tools")
            response.raise_for_status()
        payload = response.json()
        return [MCPTool(**tool) for tool in payload.get("tools", [])]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/tools/{name}/invoke",
                json={"arguments": arguments},
            )
            response.raise_for_status()
        payload = response.json()
        return payload.get("result")

    async def list_examples(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/examples")
            response.raise_for_status()
        payload = response.json()
        return payload.get("examples", [])
