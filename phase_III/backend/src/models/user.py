"""
User model for authentication and task ownership.

CONSTITUTION COMPLIANCE (Article III):
- id: UUID type (native PostgreSQL UUID), NOT int
- Uses uuid.UUID for native DB UUID support in Neon
"""
from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.task import Task
    from src.models.conversation import Conversation


class User(SQLModel, table=True):
    """
    User model for authentication and task ownership.

    CONSTITUTION COMPLIANCE (Article III):
    - id: UUID type (native PostgreSQL UUID), NOT int
    - Uses uuid.UUID for native DB UUID support in Neon
    """
    model_config = ConfigDict(from_attributes=True)

    __tablename__ = "app_users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Native UUID primary key for PostgreSQL"
    )
    email: str = Field(unique=True, max_length=255)
    hashed_password: str = Field(max_length=255)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks with cascade delete
    tasks: List["Task"] = Relationship(
        back_populates="user",
        cascade_delete="all"
    )

    # Relationship to conversations with cascade delete (Phase III)
    conversations: List["Conversation"] = Relationship(
        back_populates="user",
        cascade_delete="all"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
