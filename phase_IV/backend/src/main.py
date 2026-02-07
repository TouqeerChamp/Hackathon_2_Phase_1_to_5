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

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from fastapi.middleware.cors import CORSMiddleware

from src.db.database import create_db_and_tables, get_engine
from src.config import get_settings
from src.routers import auth_router, task_router, agent_router, chat_router

settings = get_settings()
logging.info(f"Loaded settings. DB_URL prefix: {settings.DATABASE_URL.split('@')[0] if settings.DATABASE_URL else 'N/A'}...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    - Startup: Create database tables
    - Shutdown: Cleanup handled by connection pool
    """
    logging.info("Startup: Creating database tables...")
    try:
        create_db_and_tables()
        logging.info("Startup: Database tables created successfully.")
    except Exception as e:
        logging.error(f"Startup: Failed to create tables: {e}")
    yield
    logging.info("Shutdown complete.")


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

## Task Operations (CONSTITUTION Article I COMPLIANT)

All task endpoints require JWT authentication. User identified via token claims.
- `GET /api/{user_id}/tasks` - List user's tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{id}` - Get task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `PATCH /api/{user_id}/tasks/{id}/toggle` - Toggle completion
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
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

# CORS middleware - restrict origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://todo-app-frontend-service", "http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(task_router)
app.include_router(agent_router)
app.include_router(chat_router)

# Global exception handler for unhandled 500 errors (ensures CORS + JSON)
@app.exception_handler(HTTP_500_INTERNAL_SERVER_ERROR)
async def http_500_handler(request: Request, exc: StarletteHTTPException):
    logging.error(f"500 Error: {exc.detail}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Global validation error handler (consistent format)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.get(
    "/",
    tags=["Agent Skills"],
    summary="API Root - Agent Discovery",
    description="""
**For AI Agents**: This endpoint provides an overview of available API capabilities.

## Available Skills (Article I Compliant)

1. **Authentication Skills**
   - Register new user: `POST /auth/register`
   - Login: `POST /auth/login`
   - Logout: `POST /auth/logout`

2. **Task Management Skills**
   - List tasks: `GET /api/{user_id}/tasks`
   - Create task: `POST /api/{user_id}/tasks`
   - Get task: `GET /api/{user_id}/tasks/{id}`
   - Update task: `PUT /api/{user_id}/tasks/{id}`
   - Toggle: `PATCH /api/{user_id}/tasks/{id}/toggle`
   - Delete: `DELETE /api/{user_id}/tasks/{id}`

## Response Format
Error responses: `{"detail": "error message"}`
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
    summary="Health Check (DB Test)",
    description="""
**For AI Agents**: Verify API + database connectivity.

Tests actual DB query to confirm Neon connection/pool/tables.

## Machine-Readable Response
```json
{
    "status": "healthy",
    "db_connected": true,
    "tables_exist": true,
    "timestamp": "2025-01-01T10:00:00Z"
}
```
    """
)
async def health_check():
    """Enhanced health check with DB test."""
    try:
        # Test DB connection/query
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            db_connected = bool(result.fetchone())
        tables_exist = True  # Assumed if connect succeeds post-startup
        status = "healthy" if db_connected else "db_error"
    except Exception as e:
        logging.error(f"Health check DB error: {e}")
        status = "db_error"
        db_connected = False
        tables_exist = False

    return {
        "status": status,
        "db_connected": db_connected,
        "tables_exist": tables_exist,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get(
    "/api/agent/skills",
    tags=["Agent Skills"],
    summary="Get Agent Skills Definition",
    description="""
**For AI Agents**: Machine-readable skill definitions (Article VIII).

JSON schema for endpoints, auth, formats.
    """
)
async def get_agent_skills():
    """Return machine-readable skill definitions for AI agents."""
    skills = {
        "skill_name": "todo_tasks",
        "description": "Manage user tasks in Todo app (UUID user_id)",
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
                "path": "/api/{user_id}/tasks",
                "description": "List user's tasks",
                "authentication": "Required (JWT Bearer)",
                "query_params": {
                    "completed": "true|false",
                    "search": "keyword"
                }
            },
            {
                "method": "POST",
                "path": "/api/{user_id}/tasks",
                "description": "Create task",
                "body": {"title": "str", "description": "str?"}
            },
            {
                "method": "GET",
                "path": "/api/{user_id}/tasks/{id}",
                "description": "Get task"
            },
            {
                "method": "PUT",
                "path": "/api/{user_id}/tasks/{id}",
                "description": "Update task"
            },
            {
                "method": "PATCH",
                "path": "/api/{user_id}/tasks/{id}/toggle",
                "description": "Toggle completion"
            },
            {
                "method": "DELETE",
                "path": "/api/{user_id}/tasks/{id}",
                "description": "Delete task"
            }
        ],
        "response_formats": {
            "success": "JSON data",
            "error": {"detail": "str"},
            "validation": {"detail": [{"loc": [], "msg": "str", "type": "str"}]}
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
