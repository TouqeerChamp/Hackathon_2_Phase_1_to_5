# MCP Tools Specification (Phase III)

## Overview

This document defines the Model Context Protocol (MCP) tools for the AI Chatbot to interact with the Todo application. These tools allow the AI agent to manage tasks on behalf of authenticated users.

**Framework**: Official MCP SDK for Python
**Runner**: OpenAI Agents SDK

## Core Principles

1. **Statelessness**: Every tool call is independent
2. **User Scoping**: All operations require `user_id` for authorization
3. **SQLModel Integration**: Direct database operations via SQLModel
4. **Error Handling**: Consistent error responses for AI parsing

## MCP Server Configuration

```python
# backend/src/mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
```

## Tool Definitions

### 1. add_task

Creates a new task for a user.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of the user creating the task"
    },
    "title": {
      "type": "string",
      "maxLength": 200,
      "description": "Task title (required)"
    },
    "description": {
      "type": "string",
      "description": "Task description (optional, defaults to empty string)"
    }
  },
  "required": ["user_id", "title"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "string" },
        "title": { "type": "string" },
        "description": { "type": "string" },
        "completed": { "type": "boolean" },
        "created_at": { "type": "string", "format": "date-time" },
        "updated_at": { "type": "string", "format": "date-time" }
      }
    },
    "error": { "type": "string" }
  }
}
```

**Implementation:**
```python
@server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: UUID of the task owner
        title: Task title (max 200 chars)
        description: Optional task description

    Returns:
        Created task object or error
    """
```

---

### 2. list_tasks

Retrieves all tasks for a user with optional filtering.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of the user"
    },
    "completed": {
      "type": "boolean",
      "description": "Filter by completion status (optional)"
    },
    "search": {
      "type": "string",
      "description": "Search in title/description (optional)"
    }
  },
  "required": ["user_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "user_id": { "type": "string" },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "completed": { "type": "boolean" },
          "created_at": { "type": "string" },
          "updated_at": { "type": "string" }
        }
      }
    },
    "total": { "type": "integer" },
    "error": { "type": "string" }
  }
}
```

**Implementation:**
```python
@server.tool()
async def list_tasks(
    user_id: str,
    completed: bool | None = None,
    search: str | None = None
) -> dict:
    """
    List all tasks for a user.

    Args:
        user_id: UUID of the task owner
        completed: Optional filter by completion status
        search: Optional search string for title/description

    Returns:
        List of tasks with total count
    """
```

---

### 3. complete_task

Toggles the completion status of a task.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of the user (for authorization)"
    },
    "task_id": {
      "type": "integer",
      "description": "ID of the task to toggle"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "completed": { "type": "boolean" },
        "updated_at": { "type": "string" }
      }
    },
    "error": { "type": "string" }
  }
}
```

**Implementation:**
```python
@server.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """
    Toggle task completion status.

    Args:
        user_id: UUID of the task owner (authorization)
        task_id: ID of the task to toggle

    Returns:
        Updated task with new completion status
    """
```

---

### 4. delete_task

Deletes a task belonging to a user.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of the user (for authorization)"
    },
    "task_id": {
      "type": "integer",
      "description": "ID of the task to delete"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "message": { "type": "string" },
    "deleted_task_id": { "type": "integer" },
    "error": { "type": "string" }
  }
}
```

**Implementation:**
```python
@server.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """
    Delete a task.

    Args:
        user_id: UUID of the task owner (authorization)
        task_id: ID of the task to delete

    Returns:
        Confirmation message or error
    """
```

---

### 5. update_task

Updates a task's title and/or description.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of the user (for authorization)"
    },
    "task_id": {
      "type": "integer",
      "description": "ID of the task to update"
    },
    "title": {
      "type": "string",
      "maxLength": 200,
      "description": "New task title (optional)"
    },
    "description": {
      "type": "string",
      "description": "New task description (optional)"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "title": { "type": "string" },
        "description": { "type": "string" },
        "updated_at": { "type": "string" }
      }
    },
    "error": { "type": "string" }
  }
}
```

**Implementation:**
```python
@server.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> dict:
    """
    Update a task's title and/or description.

    Args:
        user_id: UUID of the task owner (authorization)
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Updated task object or error
    """
```

---

## Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**Error Types:**
| Error | Condition |
|-------|-----------|
| `User not found` | user_id doesn't exist in database |
| `Task not found` | task_id doesn't exist or doesn't belong to user |
| `Validation error` | Invalid input (e.g., title too long) |
| `Database error` | Connection or query failure |

---

## Database Operations

All tools use SQLModel for database operations:

```python
from sqlmodel import Session, select
from src.db.database import engine
from src.models import User, Task

def get_user(session: Session, user_id: str) -> User | None:
    """Verify user exists."""
    return session.get(User, UUID(user_id))

def get_task_for_user(session: Session, task_id: int, user_id: str) -> Task | None:
    """Get task if it belongs to user."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == UUID(user_id)
    )
    return session.exec(statement).first()
```

---

## Server Entry Point

```python
# backend/src/mcp_server.py

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("todo-mcp-server")

# Register tools...

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Usage with OpenAI Agents SDK

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# Connect to MCP server
async with MCPServerStdio(
    params={"command": "python", "args": ["backend/src/mcp_server.py"]}
) as mcp_server:
    agent = Agent(
        name="Todo Assistant",
        instructions="Help users manage their tasks.",
        mcp_servers=[mcp_server]
    )

    runner = Runner()
    result = await runner.run(agent, "List my tasks")
```

---

## Security Considerations

1. **User Isolation**: All operations are scoped to the provided `user_id`
2. **No Cross-User Access**: Tasks can only be accessed by their owner
3. **Input Validation**: All inputs are validated before database operations
4. **UUID Verification**: User IDs are validated as proper UUIDs
