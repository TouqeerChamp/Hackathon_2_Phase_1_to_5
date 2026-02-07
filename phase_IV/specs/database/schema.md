# Database Schema Specification

## Overview

This document defines the database schema using SQLModel for the Todo App with Neon PostgreSQL. **Constitution Article III**: User IDs are UUID Strings throughout the system.

## Database Configuration

- **Provider**: Neon (PostgreSQL)
- **ORM**: SQLModel (Constitution Article II compliant)
- **Connection**: Via environment variables
- **Table Prefix**: `app_` (for isolation)

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@ep-xyz.region.neon.tech/dbname?sslmode=require
JWT_SECRET=your-32-char-minimum-secret-key
```

## Tables

### Users Table

```sql
CREATE TABLE app_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tasks Table

```sql
CREATE TABLE app_tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON app_tasks(user_id);
CREATE INDEX idx_tasks_completed ON app_tasks(user_id, completed);
```

## SQLModel Classes (Constitution Article III: UUID MANDATE)

### User Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional
import uuid

class User(SQLModel, table=True):
    """User model for authentication and task ownership.

    CONSTITUTION COMPLIANCE:
    - id: str (UUID), NOT int (per Article III)
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36
    )
    email: str = Field(unique=True, max_length=255)
    hashed_password: str = Field(max_length=255)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete="all")
```

### Task Model

```python
class Task(SQLModel, table=True):
    """Task model for todo items with user relationship.

    CONSTITUTION COMPLIANCE:
    - user_id: str (UUID), NOT int (per Article III)
    - FK references User.id which is UUID
    """

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(
        foreign_key="user.id",
        on_delete="CASCADE",
        max_length=36
    )

    title: str = Field(max_length=200)
    description: str = Field(default="")
    completed: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: User = Relationship(back_populates="tasks")
```

## Pydantic Schemas (for API - UUID Compliant)

### TaskCreate

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
```

### TaskUpdate

```python
from pydantic import BaseModel, Field

class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None
```

### TaskResponse

```python
from pydantic import BaseModel, Field

class TaskResponse(BaseModel):
    """Schema for task response.

    CONSTITUTION COMPLIANCE:
    - user_id: str (UUID), NOT int
    """
    id: int
    user_id: str  # UUID as string per Article III
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
```

### UserCreate

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    """Schema for creating a user."""
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
```

### UserResponse

```python
from pydantic import BaseModel, Field

class UserResponse(BaseModel):
    """Schema for user response.

    CONSTITUTION COMPLIANCE:
    - id: str (UUID), NOT int
    """
    id: str  # UUID as string per Article III
    email: str
    created_at: datetime
```

## Database Engine Setup

```python
from sqlmodel import create_engine

DATABASE_URL = "postgresql://..."
engine = create_engine(DATABASE_URL, echo=True)

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

## Migration Strategy

1. **Initial Setup**: Create tables via SQLModel
2. **Schema Changes**: Create new tables, migrate data as needed
3. **Rollbacks**: Manual for Phase II (no Alembic)

## Constraints

1. **Cascade Delete**: When a user is deleted, all their tasks are deleted
2. **Unique Email**: No duplicate user emails allowed
3. **Required Fields**: title, user_id (UUID), completed
4. **Default Values**: description = "", completed = False
5. **UUID Compliance**: User IDs are strings, NOT integers (Article III)
