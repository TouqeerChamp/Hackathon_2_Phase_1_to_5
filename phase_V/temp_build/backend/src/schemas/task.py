"""
Pydantic schemas for Task CRUD operations.

All schemas use Pydantic v2 syntax with ConfigDict.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional task description"
    )

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task.

    All fields are optional - only provided fields will be updated.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Task description"
    )
    completed: bool | None = Field(
        default=None,
        description="Completion status"
    )

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    """
    Schema for task response.

    CONSTITUTION COMPLIANCE (Article III):
    - user_id: UUID type (native PostgreSQL UUID), NOT int
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Task ID (integer)")
    user_id: UUID = Field(..., description="Native UUID of task owner")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    completed: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""

    model_config = ConfigDict(from_attributes=True)

    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
