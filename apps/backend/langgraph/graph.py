from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

START = "__start__"
END = "__end__"


class _CompiledGraph:
    def __init__(self, nodes: dict[str, Callable], edges: dict[str, str]) -> None:
        self.nodes = nodes
        self.edges = edges

    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
        current = self.edges[START]
        while current != END:
            node = self.nodes[current]
            result = node(state)
            if isinstance(result, Awaitable):
                state = await result
            else:
                state = result
            current = self.edges[current]
        return state


class StateGraph:
    def __init__(self, _state_type):
        self._nodes: dict[str, Callable] = {}
        self._edges: dict[str, str] = {}

    def add_node(self, name: str, node: Callable):
        self._nodes[name] = node

    def add_edge(self, source: str, dest: str):
        self._edges[source] = dest

    def compile(self) -> _CompiledGraph:
        return _CompiledGraph(self._nodes, self._edges)
