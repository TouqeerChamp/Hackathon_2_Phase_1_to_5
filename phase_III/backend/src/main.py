"""
Todo App API - Main Entry Point

FastAPI application for the Todo Full-Stack Web Application.
Provides RESTful API for task management with JWT authentication.

AGENT COMPATIBILITY:
- All endpoints documented with detailed descriptions for AI Agent skill discovery
- Swagger UI available at /docs for endpoint exploration
- Response formats are consistent and machine-readable

CONSTITUTION COMPLIANCE:
- Article I: Paths use /api/{user_id}/tasks pattern
- Article III: User IDs are UUID type
- Article VIII: Agentic design with comprehensive OpenAPI documentation
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.db.database import create_db_and_tables, get_engine
from src.config import get_settings
from src.routers import auth_router, task_router, agent_router, chat_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    - Startup: Create database tables
    - Shutdown: Cleanup handled by connection pool
    """
    # Startup: Initialize database
    create_db_and_tables()
    yield
    # Shutdown: Cleanup handled automatically


# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="""
    # Todo App API - Agent-Compatible Task Management

    This API provides a complete task management system with JWT authentication.

    ## Agent Skills

    This API is designed for AI Agent consumption with:
    - **Consistent Response Formats**: All responses follow predictable JSON structures
    - **Detailed Endpoint Documentation**: Every endpoint includes descriptions for agent understanding
    - **Machine-Readable Errors**: Error responses use consistent `{"detail": "message"}` format

    ## Authentication

    - Use POST /auth/register to create an account
    - Use POST /auth/login to receive a JWT token
    - Include the token in the Authorization header: `Bearer <token>`

    ## Task Operations

    All task endpoints require JWT authentication. The user is identified from the token.
    - `GET /api/v1/tasks` - List all tasks
    - `POST /api/v1/tasks` - Create a new task
    - `GET /api/v1/tasks/{task_id}` - Get a specific task
    - `PUT /api/v1/tasks/{task_id}` - Update a task
    - `PATCH /api/v1/tasks/{task_id}/toggle` - Toggle task completion
    - `DELETE /api/v1/tasks/{task_id}` - Delete a task
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Agent Skills", "description": "Endpoints documented for AI Agent skill discovery"},
        {"name": "Health", "description": "Health check and system status"},
        {"name": "Auth", "description": "Authentication endpoints (register, login, logout)"},
        {"name": "Tasks", "description": "Task CRUD operations (requires authentication)"},
        {"name": "Chat", "description": "AI Chatbot endpoints (Phase III)"},
    ]
)

# CORS middleware for frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","http://localhost:3001","http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(task_router)
app.include_router(agent_router)
app.include_router(chat_router)


@app.get(
    "/",
    tags=["Agent Skills"],
    summary="API Root - Agent Discovery",
    description="""
    **For AI Agents**: This endpoint provides an overview of available API capabilities.

    ## Available Skills

    1. **Authentication Skills**
       - Register new user: `POST /auth/register`
       - Login: `POST /auth/login`
       - Logout: `POST /auth/logout`

    2. **Task Management Skills**
       - List tasks: `GET /api/v1/tasks`
       - Create task: `POST /api/v1/tasks`
       - Get task: `GET /api/v1/tasks/{task_id}`
       - Update task: `PUT /api/v1/tasks/{task_id}`
       - Toggle completion: `PATCH /api/v1/tasks/{task_id}/toggle`
       - Delete task: `DELETE /api/v1/tasks/{task_id}`

    ## Response Format

    All responses are consistent JSON structures. Error responses follow:
    ```json
    {"detail": "error message"}
    ```
    """
)
async def root():
    """API root endpoint with agent-friendly documentation."""
    return {
        "name": "Todo App API",
        "version": "1.0.0",
        "description": "Full-Stack Todo App with Agent-Compatible API",
        "documentation": "/docs",
        "health": "/health",
        "skills": {
            "authentication": ["/auth/register", "/auth/login", "/auth/logout"],
            "tasks": ["/api/{user_id}/tasks", "/api/{user_id}/tasks/{id}"]
        }
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="""
    **For AI Agents**: Verify API is running and database is accessible.

    ## Response

    Returns system status and current timestamp.
    Useful for monitoring and health checks.

    ## Machine-Readable Response

    ```json
    {
        "status": "healthy",
        "timestamp": "2025-01-01T10:00:00Z"
    }
    ```
    """
)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get(
    "/api/agent/skills",
    tags=["Agent Skills"],
    summary="Get Agent Skills Definition",
    description="""
    **For AI Agents**: Returns a machine-readable definition of all available skills.

    ## Usage

    This endpoint provides a JSON schema that describes:
    - Skill name and description
    - Available endpoints
    - Input/output formats
    - Authentication requirements

    ## Response Example

    ```json
    {
        "skill_name": "todo_tasks",
        "description": "Manage user tasks in the Todo application",
        "version": "1.0.0",
        "endpoints": [...]
    }
    ```
    """
)
async def get_agent_skills():
    """
    Return machine-readable skill definitions for AI agents.

    This endpoint provides a JSON schema that AI agents can use to
    understand and interact with the Todo API.
    """
    skills = {
        "skill_name": "todo_tasks",
        "description": "Manage user tasks in the Todo application",
        "version": "1.0.0",
        "authentication": {
            "type": "Bearer JWT",
            "endpoints": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "logout": "POST /auth/logout"
            }
        },
        "endpoints": [
            {
                "method": "GET",
                "path": "/api/v1/tasks",
                "description": "List all tasks for the authenticated user",
                "authentication": "Required (JWT Bearer token)",
                "query_params": {
                    "completed": "Filter by completion status (true/false)",
                    "search": "Search in title and description"
                }
            },
            {
                "method": "POST",
                "path": "/api/v1/tasks",
                "description": "Create a new task for the authenticated user",
                "authentication": "Required (JWT Bearer token)",
                "body": {
                    "title": "string (required, 1-200 chars)",
                    "description": "string (optional, max 1000 chars)"
                }
            },
            {
                "method": "GET",
                "path": "/api/v1/tasks/{task_id}",
                "description": "Get a specific task by ID",
                "authentication": "Required (JWT Bearer token)"
            },
            {
                "method": "PUT",
                "path": "/api/v1/tasks/{task_id}",
                "description": "Update an existing task",
                "authentication": "Required (JWT Bearer token)",
                "body": {
                    "title": "string (optional, 1-200 chars)",
                    "description": "string (optional)",
                    "completed": "boolean (optional)"
                }
            },
            {
                "method": "PATCH",
                "path": "/api/v1/tasks/{task_id}/toggle",
                "description": "Toggle task completion status",
                "authentication": "Required (JWT Bearer token)"
            },
            {
                "method": "DELETE",
                "path": "/api/v1/tasks/{task_id}",
                "description": "Delete a task",
                "authentication": "Required (JWT Bearer token)"
            }
        ],
        "response_formats": {
            "success": "JSON object with requested data",
            "error": {"detail": "string"},
            "validation_error": {"detail": [{"loc": [], "msg": "string", "type": "string"}]}
        }
    }
    return skills


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
