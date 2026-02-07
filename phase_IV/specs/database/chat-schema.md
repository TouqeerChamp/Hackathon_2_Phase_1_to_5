# Chat Schema Specification (Phase III)

## Overview

This document defines the database schema for AI Chatbot functionality using SQLModel for the Todo App with Neon PostgreSQL. These models extend the existing schema without modifying User or Task models.

**Constitution Compliance**:
- Article III: User IDs are UUID throughout the system
- Article II: Using SQLModel (NOT SQLAlchemy/Drizzle)

## New Tables

### Conversations Table

Stores chat conversation sessions linked to users.

```sql
CREATE TABLE app_conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON app_conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON app_conversations(user_id, updated_at DESC);
```

### Messages Table

Stores individual messages within conversations.

```sql
CREATE TABLE app_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES app_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON app_messages(conversation_id);
CREATE INDEX idx_messages_created_at ON app_messages(conversation_id, created_at);
```

## SQLModel Classes

### Conversation Model

```python
from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID

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
```

### Message Model

```python
from datetime import datetime
from typing import TYPE_CHECKING

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
```

## Relationships Diagram

```
┌─────────────────┐
│   app_users     │
│   (User)        │
│   id: UUID (PK) │
├─────────────────┤
│ - email         │
│ - hashed_pass   │
│ - created_at    │
│ - updated_at    │
└────────┬────────┘
         │
         │ 1:N (CASCADE DELETE)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────────────┐    ┌─────────────────────┐
│   app_tasks     │    │  app_conversations  │
│   (Task)        │    │  (Conversation)     │
│   id: int (PK)  │    │  id: int (PK)       │
│   user_id: UUID │    │  user_id: UUID (FK) │
├─────────────────┤    ├─────────────────────┤
│ - title         │    │ - title             │
│ - description   │    │ - created_at        │
│ - completed     │    │ - updated_at        │
│ - created_at    │    └──────────┬──────────┘
│ - updated_at    │               │
└─────────────────┘               │ 1:N (CASCADE DELETE)
                                  │
                                  ▼
                    ┌─────────────────────┐
                    │    app_messages     │
                    │    (Message)        │
                    │    id: int (PK)     │
                    │ conversation_id: int│
                    ├─────────────────────┤
                    │ - role              │
                    │ - content           │
                    │ - created_at        │
                    └─────────────────────┘
```

## User Model Update Required

The User model needs a new relationship to conversations:

```python
# Add to User model
conversations: List["Conversation"] = Relationship(
    back_populates="user",
    cascade_delete="all"
)
```

## Migration Notes

- Tables are created automatically via `SQLModel.metadata.create_all(engine)`
- Existing `app_users` and `app_tasks` tables are NOT modified
- New tables will be created on next application startup
- Cascade delete ensures data integrity when users are deleted
