"""
Chat router for AI Chatbot functionality.

Provides the POST /api/{user_id}/chat endpoint for interacting with
the AI assistant using Gemini 2.5 Flash via OpenAI-compatible endpoint.

CONSTITUTION COMPLIANCE:
- Article I: Path uses /api/{user_id}/chat pattern
- Article III: User IDs are UUID type
"""
import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from openai import OpenAI

from src.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
from src.db.database import get_db
from src.models import User, Conversation, Message, Task
from src.schemas.chat import ChatRequest, ChatResponse, MessageResponse

router = APIRouter(
    prefix="/api",
    tags=["Chat", "Agent Skills"]
)

settings = get_settings()

# System instructions for the AI agent
SYSTEM_INSTRUCTIONS = """You are a helpful Todo assistant. You help users manage their tasks.

Available actions you can perform:
- Add new tasks: Create tasks with a title and optional description
- List tasks: Show all tasks, or filter by completed/incomplete status
- Complete tasks: Mark tasks as done or toggle their completion status
- Update tasks: Change task title or description
- Delete tasks: Remove tasks permanently

Guidelines:
- Be concise and helpful in your responses
- When listing tasks, format them clearly with task ID, title, and status
- Confirm successful operations to the user
- If an error occurs, explain it simply and suggest what to do
- You can only manage tasks for the current user

When the user asks to see their tasks, list them in a readable format like:
📋 Your Tasks:
1. [ID: 1] Buy groceries - ⬜ incomplete
2. [ID: 2] Call mom - ✅ completed
"""


def get_user_or_404(session: Session, user_id: UUID) -> User:
    """Get user by ID or raise 404."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def get_conversation_for_user(
    session: Session,
    conversation_id: int,
    user_id: UUID
) -> Conversation | None:
    """Get conversation if it belongs to the user."""
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    return session.exec(statement).first()


def fetch_message_history(
    session: Session,
    conversation_id: int,
    limit: int = 10
) -> list[dict]:
    """
    Fetch the last N messages from a conversation.
    Returns messages in chronological order.
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = session.exec(statement).all()

    # Reverse to get chronological order
    messages = list(reversed(messages))

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


def create_conversation(session: Session, user_id: UUID, title: str = "New Conversation") -> Conversation:
    """Create a new conversation for the user."""
    conversation = Conversation(
        user_id=user_id,
        title=title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def store_message(
    session: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """Store a message in the database."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def update_conversation_timestamp(session: Session, conversation: Conversation):
    """Update the conversation's updated_at timestamp."""
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()


# ============================================================================
# Tool Functions for the Agent
# ============================================================================

def build_tools_for_user(user_id: str):
    """Build tool definitions for OpenAI function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (required)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description (optional)"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the user. Can filter by completion status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "type": "boolean",
                            "description": "Filter by completion status (optional)"
                        },
                        "search": {
                            "type": "string",
                            "description": "Search in title/description (optional)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Toggle the completion status of a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to toggle"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's title and/or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]


# ============================================================================
# Tool Execution Functions
# ============================================================================

def execute_add_task(session: Session, user_id: UUID, args: dict) -> str:
    """Execute add_task tool."""
    title = args.get("title", "").strip()
    description = args.get("description", "")

    if not title:
        return json.dumps({"success": False, "error": "Title is required"})

    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    return json.dumps({
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }
    })


def execute_list_tasks(session: Session, user_id: UUID, args: dict) -> str:
    """Execute list_tasks tool."""
    completed_filter = args.get("completed")
    search = args.get("search", "").strip()

    statement = select(Task).where(Task.user_id == user_id)

    if completed_filter is not None:
        statement = statement.where(Task.completed == completed_filter)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            (Task.title.ilike(search_pattern)) |
            (Task.description.ilike(search_pattern))
        )

    statement = statement.order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()

    tasks_list = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }
        for task in tasks
    ]

    return json.dumps({
        "success": True,
        "tasks": tasks_list,
        "total": len(tasks_list)
    })


def execute_complete_task(session: Session, user_id: UUID, args: dict) -> str:
    """Execute complete_task tool."""
    task_id = args.get("task_id")

    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        return json.dumps({"success": False, "error": f"Task {task_id} not found"})

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

    return json.dumps({
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "completed": task.completed
        }
    })


def execute_delete_task(session: Session, user_id: UUID, args: dict) -> str:
    """Execute delete_task tool."""
    task_id = args.get("task_id")

    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        return json.dumps({"success": False, "error": f"Task {task_id} not found"})

    task_title = task.title
    session.delete(task)
    session.commit()

    return json.dumps({
        "success": True,
        "message": f"Task '{task_title}' (ID: {task_id}) deleted successfully"
    })


def execute_update_task(session: Session, user_id: UUID, args: dict) -> str:
    """Execute update_task tool."""
    task_id = args.get("task_id")
    new_title = args.get("title")
    new_description = args.get("description")

    if new_title is None and new_description is None:
        return json.dumps({"success": False, "error": "At least title or description must be provided"})

    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        return json.dumps({"success": False, "error": f"Task {task_id} not found"})

    if new_title is not None:
        task.title = new_title.strip()
    if new_description is not None:
        task.description = new_description

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

    return json.dumps({
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }
    })


def execute_tool(session: Session, user_id: UUID, tool_name: str, args: dict) -> str:
    """Execute a tool by name."""
    tool_handlers = {
        "add_task": execute_add_task,
        "list_tasks": execute_list_tasks,
        "complete_task": execute_complete_task,
        "delete_task": execute_delete_task,
        "update_task": execute_update_task
    }

    handler = tool_handlers.get(tool_name)
    if not handler:
        return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})

    return handler(session, user_id, args)


# ============================================================================
# Chat Endpoint
# ============================================================================

@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    summary="Chat with AI Assistant",
    description="""
    Send a message to the AI chatbot and receive a response.

    **For AI Agents**: This endpoint enables natural language interaction with
    task management. The assistant can create, list, update, complete, and
    delete tasks based on user requests.

    ## Conversation Flow

    1. **New Conversation**: Omit `conversation_id` to start fresh
    2. **Continue Conversation**: Include `conversation_id` to maintain context

    ## Examples

    - "Show me my tasks"
    - "Add a task to buy groceries"
    - "Mark task 1 as done"
    - "Delete task 2"
    - "Show me incomplete tasks"
    """
)
async def chat(
    user_id: UUID,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Process a chat message and return AI response.

    Args:
        user_id: UUID of the user
        request: Chat request with optional conversation_id and message

    Returns:
        ChatResponse with conversation_id, assistant message, and timestamp
    """
    # Verify user exists
    user = get_user_or_404(db, user_id)

    # Get or create conversation
    if request.conversation_id:
        conversation = get_conversation_for_user(db, request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
    else:
        # Create new conversation with first few words of message as title
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        conversation = create_conversation(db, user_id, title)

    # Fetch message history (last 10 messages)
    history = fetch_message_history(db, conversation.id, limit=10)

    # Store user message
    store_message(db, conversation.id, "user", request.message)

    # Build messages for Gemini (OpenAI-compatible format)
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]
    messages.extend(history)
    messages.append({"role": "user", "content": request.message})

    # Initialize Gemini client via OpenAI-compatible endpoint
    logger.info(f"Initializing Gemini client for user {user_id}")
    client = OpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Build tools
    tools = build_tools_for_user(str(user_id))

    try:
        # Run the agent loop
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            try:
                # Call Gemini via OpenAI-compatible API
                response = client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None
                )
                logger.info(f"Gemini response received")
            except Exception as api_error:
                logger.error(f"Gemini API error: {type(api_error).__name__}: {str(api_error)}")
                raise api_error

            assistant_message = response.choices[0].message

            # Check if the model wants to call tools
            if assistant_message.tool_calls:
                logger.info(f"Tool calls requested: {[tc.function.name for tc in assistant_message.tool_calls]}")
                # Add assistant message with tool calls to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as json_err:
                        logger.error(f"Failed to parse tool arguments: {tool_call.function.arguments}")
                        tool_args = {}

                    # Execute the tool
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    tool_result = execute_tool(db, user_id, tool_name, tool_args)
                    logger.info(f"Tool result: {tool_result[:100]}...")

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
            else:
                # No more tool calls, we have the final response
                logger.info("No tool calls, final response received")
                break

        # Get the final assistant response
        final_content = assistant_message.content or "I've completed the requested action."
        logger.info(f"Final response: {final_content[:100]}...")

        # Store assistant message
        assistant_msg = store_message(db, conversation.id, "assistant", final_content)

        # Update conversation timestamp
        update_conversation_timestamp(db, conversation)

        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse(
                role="assistant",
                content=final_content
            ),
            created_at=assistant_msg.created_at
        )

    except Exception as e:
        # Log the full error with traceback
        logger.error(f"Chat error: {type(e).__name__}: {str(e)}", exc_info=True)

        # Store error message
        error_content = f"I encountered an error while processing your request. Please try again."
        try:
            store_message(db, conversation.id, "assistant", error_content)
        except Exception as db_error:
            logger.error(f"Failed to store error message: {db_error}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {type(e).__name__}: {str(e)}"
        )


@router.get(
    "/{user_id}/conversations",
    summary="List User Conversations",
    description="Get all conversations for a user, ordered by most recent first."
)
async def list_conversations(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """List all conversations for a user."""
    # Verify user exists
    get_user_or_404(db, user_id)

    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = db.exec(statement).all()

    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ],
        "total": len(conversations)
    }


@router.get(
    "/{user_id}/conversations/{conversation_id}/messages",
    summary="Get Conversation Messages",
    description="Get all messages in a conversation."
)
async def get_conversation_messages(
    user_id: UUID,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation."""
    # Verify user exists
    get_user_or_404(db, user_id)

    # Verify conversation belongs to user
    conversation = get_conversation_for_user(db, conversation_id, user_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied"
        )

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = db.exec(statement).all()

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ],
        "total": len(messages)
    }
