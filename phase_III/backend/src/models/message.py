"""
Message model for individual chat messages.

Roles:
- "user": Messages from the human user
- "assistant": Messages from the AI assistant
- "system": System messages (optional, for context)
"""
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message model for individual chat messages.

    Roles:
    - "user": Messages from the human user
    - "assistant": Messages from the AI assistant
    - "system": System messages (optional, for context)
    """
    model_config = ConfigDict(from_attributes=True)

    __tablename__ = "app_messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="app_conversations.id",
        description="ID of the conversation this message belongs to"
    )
    role: str = Field(
        max_length=20,
        description="Message role: 'user', 'assistant', or 'system'"
    )
    content: str = Field(description="Message content text")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    conversation: "Conversation" = Relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
