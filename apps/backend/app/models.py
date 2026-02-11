from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class PlannedTask:
    id: int
    title: str
    description: str
    tool_name: str | None = None
    tool_input: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(slots=True)
class AgentPlan:
    goal: str
    tasks: list[PlannedTask]

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "tasks": [task.to_dict() for task in self.tasks],
        }


@dataclass(slots=True)
class MCPTool:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
