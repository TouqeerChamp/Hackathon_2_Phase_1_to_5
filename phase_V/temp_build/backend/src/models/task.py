"""
Task model for todo items with user relationship.

CONSTITUTION COMPLIANCE (Article III):
- user_id: UUID type (native PostgreSQL UUID FK), NOT int
- FK references User.id which is native UUID
"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.user import User


class Task(SQLModel, table=True):
    """
    Task model for todo items with user relationship.

    CONSTITUTION COMPLIANCE (Article III):
    - user_id: UUID type (native PostgreSQL UUID FK), NOT int
    - FK references User.id which is native UUID
    """
    model_config = ConfigDict(from_attributes=True)

    __tablename__ = "app_tasks"

    # Task ID is integer (auto-incrementing) - SQLModel handles autoincrement automatically
    id: int | None = Field(default=None, primary_key=True)

    # User ID is native UUID (foreign key) - Article III compliant
    # Cascade delete is handled by User.tasks relationship (cascade_delete="all")
    user_id: UUID = Field(
        foreign_key="app_users.id",
        description="Native UUID of the user who owns this task"
    )

    title: str = Field(max_length=200, description="Task title")
    description: str = Field(default="", description="Task description")
    completed: bool = Field(default=False, description="Completion status")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: "User" = Relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, user_id={self.user_id})>"
