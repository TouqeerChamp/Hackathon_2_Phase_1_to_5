"""
MCP Server for Todo Application.

Provides tools for AI agents to manage tasks via the Model Context Protocol.
Uses the Official MCP SDK for Python.

Tools:
- add_task: Create a new task
- list_tasks: List user's tasks with optional filters
- complete_task: Toggle task completion status
- delete_task: Delete a task
- update_task: Update task title/description
"""
import asyncio
import sys
import os
from datetime import datetime
from uuid import UUID

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

from sqlmodel import Session, select
from src.db.database import engine
from src.models import User, Task


# Initialize MCP Server
server = Server("todo-mcp-server")


# ============================================================================
# Helper Functions
# ============================================================================

def validate_uuid(user_id: str) -> UUID | None:
    """Validate and convert string to UUID."""
    try:
        return UUID(user_id)
    except (ValueError, TypeError):
        return None


def get_user(session: Session, user_id: UUID) -> User | None:
    """Get user by UUID."""
    return session.get(User, user_id)


def get_task_for_user(session: Session, task_id: int, user_id: UUID) -> Task | None:
    """Get task if it belongs to the specified user."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return session.exec(statement).first()


def task_to_dict(task: Task) -> dict:
    """Convert Task model to dictionary."""
    return {
        "id": task.id,
        "user_id": str(task.user_id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


def error_response(message: str) -> dict:
    """Create standardized error response."""
    return {"success": False, "error": message}


def success_response(**kwargs) -> dict:
    """Create standardized success response."""
    return {"success": True, **kwargs}


# ============================================================================
# Tool Handlers
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task for a user. Requires user_id (UUID) and title. Description is optional.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user creating the task"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required, max 200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional)"
                    }
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List all tasks for a user. Can filter by completion status or search in title/description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Filter by completion status (optional)"
                    },
                    "search": {
                        "type": "string",
                        "description": "Search string for title/description (optional)"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Toggle the completion status of a task. If completed, marks as incomplete; if incomplete, marks as completed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user (for authorization)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to toggle"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task. The task must belong to the specified user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user (for authorization)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update a task's title and/or description. At least one of title or description must be provided.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user (for authorization)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional, max 200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional)"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    import json

    try:
        if name == "add_task":
            result = await handle_add_task(arguments)
        elif name == "list_tasks":
            result = await handle_list_tasks(arguments)
        elif name == "complete_task":
            result = await handle_complete_task(arguments)
        elif name == "delete_task":
            result = await handle_delete_task(arguments)
        elif name == "update_task":
            result = await handle_update_task(arguments)
        else:
            result = error_response(f"Unknown tool: {name}")
    except Exception as e:
        result = error_response(f"Internal error: {str(e)}")

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


# ============================================================================
# Tool Implementations
# ============================================================================

async def handle_add_task(args: dict) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: UUID of the task owner
        title: Task title (required)
        description: Task description (optional)

    Returns:
        Created task or error
    """
    user_id_str = args.get("user_id")
    title = args.get("title", "").strip()
    description = args.get("description", "")

    # Validate user_id
    user_uuid = validate_uuid(user_id_str)
    if not user_uuid:
        return error_response("Invalid user_id format. Must be a valid UUID.")

    # Validate title
    if not title:
        return error_response("Title is required.")
    if len(title) > 200:
        return error_response("Title must be 200 characters or less.")

    with Session(engine) as session:
        # Verify user exists
        user = get_user(session, user_uuid)
        if not user:
            return error_response(f"User not found: {user_id_str}")

        # Create task
        task = Task(
            user_id=user_uuid,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return success_response(task=task_to_dict(task))


async def handle_list_tasks(args: dict) -> dict:
    """
    List all tasks for a user.

    Args:
        user_id: UUID of the task owner
        completed: Optional filter by completion status
        search: Optional search string

    Returns:
        List of tasks with total count
    """
    user_id_str = args.get("user_id")
    completed_filter = args.get("completed")
    search = args.get("search", "").strip()

    # Validate user_id
    user_uuid = validate_uuid(user_id_str)
    if not user_uuid:
        return error_response("Invalid user_id format. Must be a valid UUID.")

    with Session(engine) as session:
        # Verify user exists
        user = get_user(session, user_uuid)
        if not user:
            return error_response(f"User not found: {user_id_str}")

        # Build query
        statement = select(Task).where(Task.user_id == user_uuid)

        # Apply completed filter
        if completed_filter is not None:
            statement = statement.where(Task.completed == completed_filter)

        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            statement = statement.where(
                (Task.title.ilike(search_pattern)) |
                (Task.description.ilike(search_pattern))
            )

        # Order by created_at descending
        statement = statement.order_by(Task.created_at.desc())

        tasks = session.exec(statement).all()
        tasks_list = [task_to_dict(task) for task in tasks]

        return success_response(tasks=tasks_list, total=len(tasks_list))


async def handle_complete_task(args: dict) -> dict:
    """
    Toggle task completion status.

    Args:
        user_id: UUID of the task owner
        task_id: ID of the task to toggle

    Returns:
        Updated task or error
    """
    user_id_str = args.get("user_id")
    task_id = args.get("task_id")

    # Validate user_id
    user_uuid = validate_uuid(user_id_str)
    if not user_uuid:
        return error_response("Invalid user_id format. Must be a valid UUID.")

    # Validate task_id
    if task_id is None or not isinstance(task_id, int):
        return error_response("task_id must be an integer.")

    with Session(engine) as session:
        # Get task for user
        task = get_task_for_user(session, task_id, user_uuid)
        if not task:
            return error_response(f"Task not found or access denied: {task_id}")

        # Toggle completion
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return success_response(
            task={
                "id": task.id,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        )


async def handle_delete_task(args: dict) -> dict:
    """
    Delete a task.

    Args:
        user_id: UUID of the task owner
        task_id: ID of the task to delete

    Returns:
        Confirmation or error
    """
    user_id_str = args.get("user_id")
    task_id = args.get("task_id")

    # Validate user_id
    user_uuid = validate_uuid(user_id_str)
    if not user_uuid:
        return error_response("Invalid user_id format. Must be a valid UUID.")

    # Validate task_id
    if task_id is None or not isinstance(task_id, int):
        return error_response("task_id must be an integer.")

    with Session(engine) as session:
        # Get task for user
        task = get_task_for_user(session, task_id, user_uuid)
        if not task:
            return error_response(f"Task not found or access denied: {task_id}")

        # Delete task
        session.delete(task)
        session.commit()

        return success_response(
            message=f"Task {task_id} deleted successfully.",
            deleted_task_id=task_id
        )


async def handle_update_task(args: dict) -> dict:
    """
    Update a task's title and/or description.

    Args:
        user_id: UUID of the task owner
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Updated task or error
    """
    user_id_str = args.get("user_id")
    task_id = args.get("task_id")
    new_title = args.get("title")
    new_description = args.get("description")

    # Validate user_id
    user_uuid = validate_uuid(user_id_str)
    if not user_uuid:
        return error_response("Invalid user_id format. Must be a valid UUID.")

    # Validate task_id
    if task_id is None or not isinstance(task_id, int):
        return error_response("task_id must be an integer.")

    # Check if at least one field to update
    if new_title is None and new_description is None:
        return error_response("At least one of 'title' or 'description' must be provided.")

    # Validate title length
    if new_title is not None and len(new_title) > 200:
        return error_response("Title must be 200 characters or less.")

    with Session(engine) as session:
        # Get task for user
        task = get_task_for_user(session, task_id, user_uuid)
        if not task:
            return error_response(f"Task not found or access denied: {task_id}")

        # Update fields
        if new_title is not None:
            task.title = new_title.strip()
        if new_description is not None:
            task.description = new_description

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return success_response(task=task_to_dict(task))


# ============================================================================
# Server Entry Point
# ============================================================================

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
