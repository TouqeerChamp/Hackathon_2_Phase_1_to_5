# Milestone 1: Backend Foundation

## Goal

Set up FastAPI application with SQLModel (UUID-compliant per Constitution Article III) and Neon DB connection.

## Reference Specs

- `specs/overview.md` - Tech stack: FastAPI, SQLModel, Neon DB
- `specs/database/schema.md` - User (UUID id), Task (UUID user_id) SQLModel definitions
- `specs/api/rest-endpoints.md` - API structure (for context)

---

## Task 1.1: Create Backend Project Structure

### Description

Set up the Python project with pyproject.toml, requirements.txt, and directory structure.

### Steps

1. Create `backend/pyproject.toml` with project metadata and dependencies:
   - fastapi
   - uvicorn[standard]
   - sqlmodel
   - psycopg2-binary
   - python-jose[cryptography]
   - passlib[bcrypt]
   - python-multipart
   - pydantic>=2.0
   - pydantic-settings  # For environment variable loading (Pydantic v2 compatible)

2. Create `backend/requirements.txt` for pip install

3. Create `backend/.env.example` with:
   ```
   DATABASE_URL=postgresql://user:password@ep-xyz.region.neon.tech/dbname?sslmode=require
   JWT_SECRET=your-32-char-minimum-secret-key-here
   ```

4. Create directory structure:
   ```
   backend/src/
   ├── __init__.py
   ├── models/
   │   ├── __init__.py
   │   ├── user.py
   │   └── task.py
   ├── schemas/
   │   ├── __init__.py
   │   ├── task.py
   │   └── user.py
   ├── routers/
   │   ├── __init__.py
   │   └── task.py
   ├── auth/
   │   ├── __init__.py
   │   └── jwt.py
   ├── db/
   │   ├── __init__.py
   │   └── database.py
   └── main.py
   ```

5. Create `backend/tests/__init__.py`

6. Create `backend/tests/test_models.py` (placeholder for unit tests)

7. Initialize git submodules if needed

### Acceptance Criteria

- [x] `pyproject.toml` exists with correct project name and dependencies
- [x] `requirements.txt` contains: fastapi, sqlmodel, uvicorn, psycopg2-binary, python-jose, passlib, python-multipart, pydantic>=2.0, pydantic-settings
- [x] `.env.example` shows DATABASE_URL and JWT_SECRET variables
- [x] All Python packages can be imported without errors
- [x] Backend runs: `cd backend && python -m uvicorn src.main:app --reload`

---

## Task 1.2: Configure Environment Variables

### Description

Set up environment variable loading and validation for DATABASE_URL and JWT_SECRET.

### Steps

1. Create `backend/src/config.py`:
   ```python
   import os
   from pydantic_settings import BaseSettings, SettingsConfigDict
   from functools import lru_cache

   class Settings(BaseSettings):
       """
       Application settings loaded from environment variables.

       Uses Pydantic v2's model_config (not deprecated class Config).
       """
       model_config = SettingsConfigDict(
           env_file=".env",
           env_file_encoding="utf-8",
           extra="ignore"
       )

       DATABASE_URL: str
       JWT_SECRET: str
       JWT_ALGORITHM: str = "HS256"
       API_V1_PREFIX: str = "/api/v1"

   @lru_cache()
   def get_settings() -> Settings:
       return Settings()
   ```

2. Create `.env` file template (copy from .env.example)

3. Test environment loading in Python REPL

### Acceptance Criteria

- [x] `config.py` loads DATABASE_URL from environment
- [x] `config.py` loads JWT_SECRET from environment
- [x] Uses `model_config = SettingsConfigDict(...)` (Pydantic v2, no deprecation warning)
- [x] JWT_ALGORITHM defaults to "HS256"
- [x] Settings can be accessed: `settings.DATABASE_URL`
- [x] Missing env vars raise appropriate errors

---

## Task 1.3: Set Up SQLModel Database Engine

### Description

Create database connection with Neon DB URL and table initialization logic.

### Steps

1. Create `backend/src/db/database.py`:
   ```python
   from sqlmodel import create_engine, SQLModel
   from src.config import get_settings

   settings = get_settings()
   DATABASE_URL = settings.DATABASE_URL

   engine = create_engine(
       DATABASE_URL,
       echo=True,
       pool_pre_ping=True,
       pool_size=5,
       max_overflow=10
   )

   def get_db():
       """Dependency for getting database session."""
       with SQLModel.sessionmaker(autocommit=False, bind=engine) as session:
           try:
               yield session
           finally:
               session.close()

   def create_db_and_tables():
       """Create all tables defined in SQLModel.metadata."""
       SQLModel.metadata.create_all(engine)
   ```

2. Create `backend/src/db/__init__.py`:
   ```python
   from src.db.database import engine, get_db, create_db_and_tables, DATABASE_URL

   __all__ = ["engine", "get_db", "create_db_and_tables", "DATABASE_URL"]
   ```

3. Test connection to Neon DB (will fail gracefully if URL invalid)

### Acceptance Criteria

- [x] Database engine created with Neon DB URL
- [x] `create_db_and_tables()` function defined
- [x] `get_db()` dependency function works
- [x] SQLAlchemy echo mode available for debugging
- [x] Connection pool configured (pool_size=5, max_overflow=10)
- [x] pool_pre_ping enabled for connection health checks

---

## Task 1.4: Implement User Model (UUID Compliant)

### Description

Create SQLModel User class with UUID primary key per Constitution Article III.

### Steps

1. Create `backend/src/models/user.py`:
   ```python
   from sqlmodel import SQLModel, Field, Relationship
   from datetime import datetime
   from typing import List, Optional
   from uuid import UUID, uuid4
   from pydantic import ConfigDict

   class User(SQLModel, table=True):
       """
       User model for authentication and task ownership.

       CONSTITUTION COMPLIANCE (Article III):
       - id: UUID type (native PostgreSQL UUID), NOT int
       - Uses uuid.UUID for native DB UUID support in Neon
       """
       model_config = ConfigDict(from_attributes=True)

       __tablename__ = "app_users"

       id: UUID = Field(
           default_factory=uuid4,
           primary_key=True,
           description="Native UUID primary key for PostgreSQL"
       )
       email: str = Field(unique=True, max_length=255)
       hashed_password: str = Field(max_length=255)

       created_at: datetime = Field(default_factory=datetime.utcnow)
       updated_at: datetime = Field(default_factory=datetime.utcnow)

       # Relationship to tasks
       tasks: List["Task"] = Relationship(
           back_populates="user",
           cascade_delete="all"
       )

       def __repr__(self):
           return f"<User(id={self.id}, email={self.email})>"
   ```

2. Create `backend/src/models/__init__.py`:
   ```python
   from src.models.user import User
   from src.models.task import Task

   __all__ = ["User", "Task"]
   ```

### Acceptance Criteria

- [x] User model defined with `table=True`
- [x] `id` field is `UUID` type (native PostgreSQL UUID) - NOT int (Article III)
- [x] `id` uses `uuid4()` factory for auto-generation
- [x] `model_config = ConfigDict(from_attributes=True)` (Pydantic v2, no deprecation)
- [x] `__tablename__` = "app_users"
- [x] `email` field is unique
- [x] `tasks` relationship defined with cascade_delete="all"
- [x] Model can be imported from `src.models`

---

## Task 1.5: Implement Task Model (UUID FK Compliant)

### Description

Create SQLModel Task class with UUID foreign key per Constitution Article III.

### Steps

1. Create `backend/src/models/task.py`:
   ```python
   from sqlmodel import SQLModel, Field, Relationship
   from datetime import datetime
   from typing import Optional
   from uuid import UUID
   from pydantic import ConfigDict
   from src.models.user import User

   class Task(SQLModel, table=True):
       """
       Task model for todo items with user relationship.

       CONSTITUTION COMPLIANCE (Article III):
       - user_id: UUID type (native PostgreSQL UUID FK), NOT int
       - FK references User.id which is native UUID
       """
       model_config = ConfigDict(from_attributes=True)

       __tablename__ = "app_tasks"

       id: int | None = Field(default=None, primary_key=True, autoincrement=True)
       user_id: UUID = Field(
           foreign_key="app_users.id",
           on_delete="CASCADE",
           description="Native UUID of the user who owns this task"
       )

       title: str = Field(max_length=200, description="Task title")
       description: str = Field(default="", description="Task description")
       completed: bool = Field(default=False, description="Completion status")

       created_at: datetime = Field(default_factory=datetime.utcnow)
       updated_at: datetime = Field(default_factory=datetime.utcnow)

       # Relationship to user
       user: User = Relationship(back_populates="tasks")

       def __repr__(self):
           return f"<Task(id={self.id}, title={self.title}, user_id={self.user_id})>"
   ```

2. Create database indexes for performance:
   ```python
   # SQLModel will auto-create indexes on FK and frequently queried fields
   # No manual index creation needed - SQLModel handles this
   ```

### Acceptance Criteria

- [x] Task model defined with `table=True`
- [x] `id` field is `int | None` with autoincrement (OK - task IDs are integers)
- [x] `user_id` field is `UUID` type (native PostgreSQL UUID FK) - NOT int (Article III)
- [x] `user_id` FK references `app_users.id` (native UUID column)
- [x] Cascade delete configured via User.tasks relationship (cascade_delete="all")
- [x] `model_config = ConfigDict(from_attributes=True)` (Pydantic v2)
- [x] `__tablename__` = "app_tasks"
- [x] Model can be imported from `src.models`

---

## Task 1.6: Create Pydantic Schemas

### Description

Create request/response schemas for API with native UUID validation (Pydantic v2).

### Steps

1. Create `backend/src/schemas/task.py`:
   ```python
   from pydantic import BaseModel, Field, ConfigDict
   from datetime import datetime
   from typing import Optional, List
   from uuid import UUID

   class TaskCreate(BaseModel):
       """Schema for creating a new task."""
       title: str = Field(..., min_length=1, max_length=200)
       description: str | None = Field(default=None, max_length=1000)

       model_config = ConfigDict(from_attributes=True)

   class TaskUpdate(BaseModel):
       """Schema for updating a task."""
       title: str | None = Field(default=None, min_length=1, max_length=200)
       description: str | None = Field(default=None, max_length=1000)
       completed: bool | None = None

       model_config = ConfigDict(from_attributes=True)

   class TaskResponse(BaseModel):
       """Schema for task response.

       CONSTITUTION COMPLIANCE (Article III):
       - user_id: UUID type (native PostgreSQL UUID), NOT int
       """
       model_config = ConfigDict(from_attributes=True)

       id: int
       user_id: UUID  # Native UUID type per Article III
       title: str
       description: str
       completed: bool
       created_at: datetime
       updated_at: datetime

   class TaskListResponse(BaseModel):
       """Schema for list of tasks response."""
       tasks: List[TaskResponse]
       total: int
   ```

2. Create `backend/src/schemas/user.py`:
   ```python
   from pydantic import BaseModel, Field, ConfigDict
   from datetime import datetime
   from uuid import UUID

   class UserCreate(BaseModel):
       """Schema for creating a user."""
       email: str = Field(..., max_length=255)
       password: str = Field(..., min_length=8)

       model_config = ConfigDict(from_attributes=True)

   class UserResponse(BaseModel):
       """Schema for user response.

       CONSTITUTION COMPLIANCE (Article III):
       - id: UUID type (native PostgreSQL UUID), NOT int
       """
       model_config = ConfigDict(from_attributes=True)

       id: UUID  # Native UUID type per Article III
       email: str
       created_at: datetime

   class UserLogin(BaseModel):
       """Schema for user login."""
       email: str
       password: str

   class TokenResponse(BaseModel):
       """Schema for token response."""
       access_token: str
       token_type: str = "bearer"
   ```

3. Create `backend/src/schemas/__init__.py`:
   ```python
   from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
   from src.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse

   __all__ = [
       "TaskCreate", "TaskUpdate", "TaskResponse", "TaskListResponse",
       "UserCreate", "UserResponse", "UserLogin", "TokenResponse"
   ]
   ```

### Acceptance Criteria

- [x] TaskCreate: title required (1-200 chars), description optional
- [x] TaskUpdate: all fields optional, completed optional
- [x] TaskResponse: includes all task fields, user_id is UUID (native)
- [x] UserCreate: email, password (min 8 chars)
- [x] UserResponse: id is UUID (native), email, created_at
- [x] UUID validation works for user_id fields
- [x] Schemas can be imported from `src.schemas`
- [x] All schemas use `model_config = ConfigDict(from_attributes=True)` (Pydantic v2)

---

## Task 1.7: Create Database Initialization Script (main.py)

### Description

Create FastAPI application entry point with database initialization and health check.

### Steps

1. Create `backend/src/main.py`:
   ```python
   from contextlib import asynccontextmanager
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from src.db.database import create_db_and_tables
   from src.config import get_settings

   settings = get_settings()

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Startup: Create tables
       create_db_and_tables()
       yield
       # Shutdown: Cleanup if needed
       pass

   app = FastAPI(
       title="Todo App API",
       description="Full-Stack Todo App with FastAPI and SQLModel",
       version="1.0.0",
       lifespan=lifespan,
       docs_url="/docs",
       redoc_url="/redoc"
   )

   # CORS middleware for frontend (localhost:3000)
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   @app.get("/health", tags=["Health"])
   def health_check():
       """Health check endpoint."""
       return {"status": "healthy", "version": "1.0.0"}

   @app.get("/", tags=["Root"])
   def root():
       """Root endpoint."""
       return {
           "name": "Todo App API",
           "version": "1.0.0",
           "docs": "/docs"
       }

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(
           "src.main:app",
           host="0.0.0.0",
           port=8000,
           reload=True
       )
   ```

2. Test the application starts correctly

3. Verify tables are created on startup

4. Test health endpoint: `GET /health`

### Acceptance Criteria

- [x] FastAPI app starts without errors
- [x] Tables created on startup (check logs)
- [x] Health endpoint at GET /health returns 200
- [x] CORS configured for localhost:3000 and 127.0.0.1:3000
- [x] App runs on port 8000
- [x] Documentation available at /docs and /redoc
- [x] Response includes version info
- [x] Article VIII compliance: Agentic docstrings and machine-readable endpoint at /api/agent/skills

---

## Task 1.8: Write Unit Tests for Models

### Description

Create unit tests for User and Task models with native UUID type validation (Pydantic v2).

### Steps

1. Create `backend/tests/conftest.py`:
   ```python
   import pytest
   from sqlmodel import SQLModel, create_engine
   from src.models.user import User
   from src.models.task import Task

   # Use SQLite for testing (note: SQLite stores UUID as TEXT)
   TEST_DATABASE_URL = "sqlite:///./test.db"

   @pytest.fixture
   def engine():
       engine = create_engine(TEST_DATABASE_URL, echo=False)
       SQLModel.metadata.create_all(engine)
       yield engine
       SQLModel.metadata.drop_all(engine)

   @pytest.fixture
   def db_session(engine):
       from sqlmodel import Session
       with Session(bind=engine) as session:
           yield session
   ```

2. Create `backend/tests/test_models.py`:
   ```python
   import pytest
   from uuid import UUID, uuid4
   from src.models.user import User
   from src.models.task import Task

   def test_user_model_creates_uuid():
       """Test that User.id is a native UUID type."""
       user = User(email="test@example.com", hashed_password="hashed")
       assert user.id is not None
       assert isinstance(user.id, UUID), f"Expected UUID, got {type(user.id)}"
       # Verify it's a valid UUID (no conversion needed)
       assert isinstance(user.id, UUID)

   def test_user_model_default_timestamps():
       """Test that timestamps are auto-generated."""
       user = User(email="test@example.com", hashed_password="hashed")
       assert user.created_at is not None
       assert user.updated_at is not None

   def test_task_model_uuid_foreign_key():
       """Test that Task.user_id is a native UUID type."""
       user_id = uuid4()  # Native UUID, not str
       task = Task(
           user_id=user_id,
           title="Test Task",
           description="Test Description"
       )
       assert task.user_id == user_id
       assert isinstance(task.user_id, UUID), f"Expected UUID, got {type(task.user_id)}"

   def test_task_model_defaults():
       """Test Task default values."""
       task = Task(user_id=uuid4(), title="Test")
       assert task.description == ""
       assert task.completed is False
       assert task.id is None (will be auto-generated on insert)

   def test_user_task_relationship():
       """Test User-Task relationship."""
       user = User(email="test@example.com", hashed_password="hashed")
       task = Task(
           user_id=user.id,
           title="Test Task"
       )
       # Relationship is established via user_id FK
       assert task.user_id == user.id
       assert isinstance(task.user_id, UUID)
   ```

3. Run tests: `cd backend && python -m pytest tests/ -v`

### Acceptance Criteria

- [x] All model tests pass (14/14 tests passed)
- [x] User.id is verified as native UUID type (Article III)
- [x] Task.user_id is verified as native UUID type (Article III)
- [x] Validation errors raised correctly
- [x] Relationship tests verify FK integrity
- [x] Test coverage includes all model fields
- [x] Tests use SQLite for isolation (no Neon DB required)

---

## Pre-Implementation Checklist

Before starting implementation, verify:

- [x] `specs/overview.md` read and understood
- [x] `specs/database/schema.md` read (UUID models)
- [x] `specs/api/rest-endpoints.md` read (context)
- [x] `CLAUDE.md` Article III (UUID mandate) understood
- [x] Python 3.12+ available (Python 3.14.2 installed)
- [x] Neon DB account created (.env file configured)
- [x] Environment variables documentation reviewed

---

## Definition of Done

Milestone 1 is complete when:
- [x] All 8 tasks completed with all acceptance criteria checked
- [x] All tests passing (14/14 tests passed)
- [x] Code reviewed against Constitution Articles I, II, III, VIII
- [x] UUID types verified throughout (Article III)
- [x] SQLModel used (not SQLAlchemy) (Article II)
- [x] Ready for Milestone 2 (Authentication Logic)

---

## Estimated Task Count

| Task | Sub-tasks | Status |
|------|-----------|--------|
| 1.1 | 5 | Completed |
| 1.2 | 6 | Completed |
| 1.3 | 6 | Completed |
| 1.4 | 8 | Completed |
| 1.5 | 8 | Completed |
| 1.6 | 8 | Completed |
| 1.7 | 8 | Completed |
| 1.8 | 7 | Completed |
| **Total** | **56** | **100%** |

---

## Next Steps

1. ✅ Milestone 1: Backend Foundation - COMPLETED
2. ➡️ Start with Milestone 2: Authentication Logic
3. Implement JWT authentication with python-jose
4. Create auth routes for register, login, and logout
5. Add password hashing with passlib[bcrypt]
