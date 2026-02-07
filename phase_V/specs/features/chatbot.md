# Chatbot Feature Specification (Phase III)

## Overview

This document defines the AI Chatbot feature that enables users to interact with their tasks through natural language. The chatbot uses the OpenAI Agents SDK with MCP tools to manage tasks.

## Core Principles

1. **Statelessness**: Each chat request is independent; history is fetched from database
2. **Context Awareness**: Last 10 messages are loaded for conversation context
3. **Agentic Control**: AI interacts with tasks exclusively via MCP Tools
4. **User Isolation**: All operations are scoped to the authenticated user

## Technology Stack

| Component | Technology |
|-----------|------------|
| AI Framework | OpenAI Agents SDK |
| Tools | MCP Server (add_task, list_tasks, complete_task, delete_task, update_task) |
| Database | SQLModel + Neon PostgreSQL |
| API | FastAPI |

## API Endpoint

### POST /api/{user_id}/chat

Sends a message to the AI chatbot and receives a response.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User's unique identifier |

**Request Body:**
```json
{
  "conversation_id": 123,        // Optional: existing conversation ID
  "message": "List my tasks"     // Required: user's message
}
```

**Response (Success - 200):**
```json
{
  "conversation_id": 123,
  "message": {
    "role": "assistant",
    "content": "Here are your tasks:\n1. Buy groceries (incomplete)\n2. Call mom (completed)"
  },
  "created_at": "2025-01-16T12:00:00Z"
}
```

**Response (Error - 400):**
```json
{
  "detail": "Message is required"
}
```

**Response (Error - 404):**
```json
{
  "detail": "User not found"
}
```

**Response (Error - 404):**
```json
{
  "detail": "Conversation not found or access denied"
}
```

## Agent Configuration

### System Instructions

```python
SYSTEM_INSTRUCTIONS = """
You are a helpful Todo assistant. You help users manage their tasks.

Available actions:
- Add new tasks
- List existing tasks (all, completed, or incomplete)
- Mark tasks as complete/incomplete
- Update task details
- Delete tasks

Always be concise and helpful. When listing tasks, format them clearly.
When a task operation succeeds, confirm it to the user.
If an error occurs, explain it simply and suggest alternatives.

Important: You can only manage tasks for the current user.
"""
```

### Agent Initialization

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

agent = Agent(
    name="Todo Assistant",
    instructions=SYSTEM_INSTRUCTIONS,
    model="gpt-4o-mini",  # Cost-effective model
    mcp_servers=[mcp_server]
)
```

## Database Operations

### Conversation Flow

1. **New Conversation** (no `conversation_id` provided):
   - Create new `Conversation` record
   - Store user message in `Message` table
   - Run agent
   - Store assistant response in `Message` table

2. **Existing Conversation** (`conversation_id` provided):
   - Verify conversation belongs to user
   - Fetch last 10 messages for context
   - Store user message in `Message` table
   - Run agent with message history
   - Store assistant response in `Message` table

### Message History Format

```python
# Fetch last 10 messages
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(10)
).all()

# Reverse to chronological order
messages = list(reversed(messages))

# Convert to agent format
history = [
    {"role": msg.role, "content": msg.content}
    for msg in messages
]
```

## MCP Server Integration

### Tool Registration

The agent connects to the MCP server which provides these tools:

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task |
| `list_tasks` | List tasks with optional filters |
| `complete_task` | Toggle task completion |
| `delete_task` | Remove a task |
| `update_task` | Modify task details |

### Tool Execution Context

All tools receive the `user_id` automatically to ensure user isolation:

```python
# Tools are called with user_id context
result = await tool.call({
    "user_id": str(user_id),
    "title": "New task"
})
```

## Schemas

### ChatRequest

```python
class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(..., min_length=1, max_length=4000)
```

### ChatResponse

```python
class ChatResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
    created_at: datetime

class MessageResponse(BaseModel):
    role: str  # "assistant"
    content: str
```

## Error Handling

| Error | HTTP Status | Condition |
|-------|-------------|-----------|
| Message required | 400 | Empty message |
| User not found | 404 | Invalid user_id |
| Conversation not found | 404 | Invalid conversation_id or wrong owner |
| Agent error | 500 | OpenAI API failure |

## Security Considerations

1. **User Verification**: User must exist in database
2. **Conversation Ownership**: Users can only access their own conversations
3. **API Key Security**: OPENAI_API_KEY stored in .env, never exposed
4. **Input Validation**: Message length limited to 4000 characters
5. **Tool Isolation**: MCP tools enforce user_id on all operations

## Environment Variables

```env
# Required for chatbot functionality
OPENAI_API_KEY=sk-...
```

## Sequence Diagram

```
User                    API                     Agent               MCP Server            Database
  |                      |                        |                      |                    |
  |-- POST /chat ------->|                        |                      |                    |
  |                      |-- Verify user ---------|-------------------->|-- Query User ----->|
  |                      |<--------------------- User exists ------------|<------------------|
  |                      |                        |                      |                    |
  |                      |-- Fetch history -------|-------------------->|-- Query Messages ->|
  |                      |<--------------------- Last 10 messages ------|<------------------|
  |                      |                        |                      |                    |
  |                      |-- Store user msg ------|-------------------->|-- INSERT Message ->|
  |                      |                        |                      |                    |
  |                      |-- Run Agent ---------->|                      |                    |
  |                      |                        |-- Call Tool -------->|                    |
  |                      |                        |                      |-- DB Operation -->|
  |                      |                        |<-- Tool Result ------|<------------------|
  |                      |<-- Agent Response -----|                      |                    |
  |                      |                        |                      |                    |
  |                      |-- Store assistant msg -|-------------------->|-- INSERT Message ->|
  |                      |                        |                      |                    |
  |<-- Response ---------|                        |                      |                    |
```

## Testing Scenarios

1. **New Conversation**: Send message without conversation_id
2. **Continue Conversation**: Send message with valid conversation_id
3. **List Tasks**: "Show me my tasks"
4. **Add Task**: "Add a task to buy milk"
5. **Complete Task**: "Mark task 1 as done"
6. **Delete Task**: "Delete task 2"
7. **Search Tasks**: "Show me incomplete tasks"
8. **Invalid User**: Send request with non-existent user_id
9. **Invalid Conversation**: Send request with wrong conversation_id
