"""
Pydantic schemas for API request/response validation.

Exports:
- User schemas: UserCreate, UserLogin, UserResponse, TokenResponse, UserRegisterResponse
- Task schemas: TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
- Chat schemas: ChatRequest, ChatResponse, MessageResponse
"""
from src.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserRegisterResponse
)
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from src.schemas.chat import ChatRequest, ChatResponse, MessageResponse

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "UserRegisterResponse",
    # Task schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    # Chat schemas
    "ChatRequest",
    "ChatResponse",
    "MessageResponse",
]
