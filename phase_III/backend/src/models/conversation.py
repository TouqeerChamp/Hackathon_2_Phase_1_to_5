"""
Conversation model for AI chat sessions.

CONSTITUTION COMPLIANCE (Article III):
- user_id: UUID type (native PostgreSQL UUID FK), NOT int
- FK references User.id which is native UUID
"""
from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model for AI chat sessions.

    CONSTITUTION COMPLIANCE (Article III):
    - user_id: UUID type (native PostgreSQL UUID FK), NOT int
    - FK references User.id which is native UUID
    """
    model_config = ConfigDict(from_attributes=True)

    __tablename__ = "app_conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(
        foreign_key="app_users.id",
        description="Native UUID of the user who owns this conversation"
    )
    title: str = Field(
        default="New Conversation",
        max_length=255,
        description="Conversation title"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete="all"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title={self.title}, user_id={self.user_id})>"
