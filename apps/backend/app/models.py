from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class PlannedTask(BaseModel):
    id: int
    title: str
    description: str
    tool_name: str | None = None
    tool_input: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any | None = None


class AgentPlan(BaseModel):
    goal: str
    tasks: list[PlannedTask]


class ChatResponse(BaseModel):
    reply: str
    plan: AgentPlan


class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
