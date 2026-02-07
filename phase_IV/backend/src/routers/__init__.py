"""
API routers for Todo App.

Exports:
- auth: Authentication endpoints (/api/v1/auth)
- tasks: Task CRUD endpoints (/api/{user_id}/tasks)
- agent: Agent skills endpoints
- chat: AI Chatbot endpoints (/api/{user_id}/chat)
"""
from src.routers.auth import router as auth_router
from src.routers.tasks import router as task_router
from src.routers.agent import router as agent_router
from src.routers.chat import router as chat_router

__all__ = ["auth_router", "task_router", "agent_router", "chat_router"]
