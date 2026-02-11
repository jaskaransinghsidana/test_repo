from __future__ import annotations

from typing import Any

from fastmcp import Client

from .models import MCPTool


class MCPClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def _with_client(self, callback):
        errors: list[str] = []
        for candidate_url in (f"{self.base_url}/mcp", self.base_url):
            try:
                async with Client(candidate_url) as client:
                    return await callback(client)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{candidate_url}: {exc}")
        raise RuntimeError("Unable to connect to MCP server. " + " | ".join(errors))

    async def list_tools(self) -> list[MCPTool]:
        async def _list(client: Client) -> list[MCPTool]:
            tools = await client.list_tools()
            normalized: list[MCPTool] = []
            for tool in tools:
                input_schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", {})
                normalized.append(
                    MCPTool(
                        name=getattr(tool, "name", "unknown"),
                        description=getattr(tool, "description", ""),
                        input_schema=input_schema or {},
                    )
                )
            return normalized

        return await self._with_client(_list)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        async def _call(client: Client) -> Any:
            result = await client.call_tool(name=name, arguments=arguments)
            if hasattr(result, "data"):
                return result.data
            if hasattr(result, "content"):
                return result.content
            return result

        return await self._with_client(_call)
