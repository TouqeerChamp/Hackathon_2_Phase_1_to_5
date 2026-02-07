# Phase II Implementation Plan

## Overview

This plan outlines the implementation roadmap for converting the Phase I CLI Todo App into a full-stack web application. **All implementation must follow the Constitution** (CLAUDE.md).

## Constitution Compliance Reference

| Article | Requirement | Status |
|---------|-------------|--------|
| Article I | API paths use `/api/{user_id}/tasks` | Required |
| Article II | Tech Stack: FastAPI + SQLModel + Neon DB / Next.js 15 + Better Auth | Required |
| Article III | User IDs are UUID Strings throughout | Required |

## Phases Summary

| Milestone | Focus | Output |
|-----------|-------|--------|
| M1 | Backend Foundation | FastAPI app with SQLModel (UUID models), Neon DB |
| M2 | Authentication Logic | JWT Shared Secret verification, Better Auth integration |
| M3 | Task CRUD API | 6 REST endpoints per `specs/api/rest-endpoints.md` |
| M4 | Frontend Foundation | Next.js 15 + Better Auth + API service layer |
| M5 | UI Integration | Task Dashboard, state management, final audit |

---

## Milestone 1: Backend Foundation

**Goal**: Set up FastAPI application with SQLModel (UUID-compliant) and Neon DB connection.

### Tasks

1.1 Create backend project structure (pyproject.toml, requirements.txt)
1.2 Configure environment variables (DATABASE_URL, JWT_SECRET)
1.3 Set up SQLModel database engine with Neon DB URL
1.4 Implement User model with UUID id (per Article III)
1.5 Implement Task model with UUID user_id FK (per Article III)
1.6 Create Pydantic schemas (TaskCreate, TaskUpdate, TaskResponse with UUID user_id)
1.7 Create database initialization script (main.py)
1.8 Write unit tests for models

### Acceptance Criteria (from Hackathon Doc)

- [ ] FastAPI application runs successfully on port 8000
- [ ] Database connection to Neon DB established
- [ ] `app_users` table created with UUID primary key
- [ ] `app_tasks` table created with UUID foreign key
- [ ] User model generates UUID via `uuid.uuid4()`
- [ ] Task model user_id is String type (not Integer)
- [ ] All Pydantic schemas validate UUID user_id correctly
- [ ] Unit tests pass for model validation

### Dependencies
- None (Starting point)

---

## Milestone 2: Authentication Logic

**Goal**: Implement JWT authentication with Shared Secret strategy for Better Auth + FastAPI integration.

### Tasks

2.1 Create JWT secret configuration from environment variable
2.2 Implement password hashing (bcrypt via passlib)
2.3 Create JWT token generation function (payload includes UUID user_id)
2.4 Implement JWT verification dependency for FastAPI (HTTPBearer)
2.5 Create auth router with POST /auth/register endpoint
2.6 Create auth router with POST /auth/login endpoint
2.7 Create auth router with POST /auth/logout endpoint
2.8 Write unit tests for auth logic (hashing, token generation, verification)

### Acceptance Criteria (from Hackathon Doc)

- [ ] JWT_SECRET environment variable used for token signing
- [ ] Passwords hashed with bcrypt, verified with passlib
- [ ] Login returns JWT token in response
- [ ] Token payload contains UUID user_id in "sub" claim
- [ ] Protected routes reject invalid tokens with 401
- [ ] /auth/register creates user with UUID id
- [ ] /auth/login validates credentials and returns token
- [ ] Auth endpoints work per `specs/api/rest-endpoints.md`
- [ ] Unit tests pass for password hashing and JWT verification

### Dependencies
- M1 (Backend Foundation) - Must complete first

---

## Milestone 3: Task CRUD API

**Goal**: Implement all task CRUD operations per `specs/api/rest-endpoints.md` with Article I path compliance.

### Tasks

3.1 Create task router with JWT dependency
3.2 Implement GET /api/{user_id}/tasks (list user's tasks)
3.3 Implement GET /api/{user_id}/tasks/{id} (get single task)
3.4 Implement POST /api/{user_id}/tasks (create task)
3.5 Implement PUT /api/{user_id}/tasks/{id} (update task)
3.6 Implement PATCH /api/{user_id}/tasks/{id}/toggle (toggle completion)
3.7 Implement DELETE /api/{user_id}/tasks/{id} (delete task)
3.8 Add query parameter filtering (completed, search)
3.9 Add user isolation (verify task.user_id matches path user_id)
3.10 Write unit tests for all endpoints

### Acceptance Criteria (from Hackathon Doc)

- [ ] All 6 endpoints use `/api/{user_id}/tasks` pattern (Article I)
- [ ] GET returns tasks array with UUID user_id in each task
- [ ] POST creates task linked to user's UUID
- [ ] PUT updates task (validates ownership via UUID)
- [ ] PATCH toggles completed status
- [ ] DELETE removes task (validates ownership via UUID)
- [ ] Query parameters `completed` and `search` work
- [ ] 401 returned for missing/invalid JWT
- [ ] 403 returned for UUID mismatch (accessing other user's task)
- [ ] 404 returned for non-existent task
- [ ] 422 returned for validation errors
- [ ] All endpoints documented match `specs/api/rest-endpoints.md`
- [ ] All unit tests pass

### Dependencies
- M1 (Backend Foundation)
- M2 (Authentication Logic) - Auth must work before CRUD

---

## Milestone 4: Frontend Foundation

**Goal**: Set up Next.js 15 application with Better Auth and API service layer.

### Tasks

4.1 Initialize Next.js 15 project (App Router, TypeScript)
4.2 Configure Better Auth with JWT_SECRET (same as backend)
4.3 Create API client utility (fetchWithAuth with UUID handling)
4.4 Set up auth context/hooks (signIn, signOut, useSession)
4.5 Create login page with email/password form
4.6 Create register page with email/password form
4.7 Create auth-protected layout wrapper
4.8 Write tests for auth flow

### Acceptance Criteria (from Hackathon Doc)

- [ ] Next.js 15 runs successfully on port 3000
- [ ] Better Auth configured with shared JWT_SECRET
- [ ] User can register with email/password
- [ ] User can login and receive JWT
- [ ] Auth session persists across page refreshes
- [ ] Protected routes redirect to login if not authenticated
- [ ] API client sends Bearer token with requests
- [ ] API client handles UUID user_id correctly
- [ ] TypeScript types match backend schemas
- [ ] Auth flow tests pass

### Dependencies
- M3 (Task CRUD API) - Backend must have endpoints ready

---

## Milestone 5: UI Integration & Validation

**Goal**: Build task management UI and integrate with backend API.

### Tasks

5.1 Create TaskList component (display all user's tasks)
5.2 Create TaskItem component (individual task with toggle, edit, delete)
5.3 Create TaskForm component (create new task)
5.4 Create TaskEdit modal (edit existing task)
5.5 Implement task state management (React Query or Context)
5.6 Connect all components to API service layer
5.7 Implement error handling UI (401, 403, 404, 422)
5.8 Add loading states and loading skeletons
5.9 Implement search and filter functionality
5.10 Final integration testing (full user flow)

### Acceptance Criteria (from Hackathon Doc)

- [ ] Task Dashboard displays all tasks for logged-in user
- [ ] Create task form adds new task via POST /api/{user_id}/tasks
- [ ] Toggle button calls PATCH /api/{user_id}/tasks/{id}/toggle
- [ ] Edit button opens modal, saves via PUT /api/{user_id}/tasks/{id}
- [ ] Delete button removes task via DELETE /api/{user_id}/tasks/{id}
- [ ] Search filter works via ?search= query parameter
- [ ] Completed filter works via ?completed= query parameter
- [ ] Error messages displayed for failed operations
- [ ] Loading states shown during API calls
- [ ] UI matches `specs/features/task-crud.md` requirements
- [ ] No TODO or FIXME comments in code
- [ ] End-to-end user flow works (register -> login -> CRUD tasks)

### Dependencies
- M4 (Frontend Foundation) - Frontend must be set up first

---

## Milestone 6: Agentic Integration (Skills)

**Goal**: Make the API fully compatible with AI Agents through comprehensive OpenAPI documentation and agent-specific skill definitions.

### Tasks

6.1 Create `backend/src/agent/` directory structure
6.2 Create `backend/src/agent/skills.py` with skill definitions for AI agents
6.3 Create `backend/src/agent/prompts.py` with system prompts for agent usage
6.4 Add detailed docstrings and OpenAPI descriptions to all endpoints
6.5 Configure Swagger UI tags for Agent discovery
6.6 Create `backend/src/agent/__init__.py` with skill exports
6.7 Write unit tests for agent skill definitions

### Acceptance Criteria (from Hackathon Doc)

- [ ] API fully documented for AI Agent skill discovery
- [ ] Every endpoint has detailed docstrings and OpenAPI descriptions
- [ ] Swagger UI (`/docs`) perfectly labeled for Agent discovery
- [ ] `backend/src/agent/` directory created with skills and prompts
- [ ] Skills defined in JSON/Schema format for agent consumption
- [ ] System prompts explain how AI should use Todo Skills
- [ ] Agent can discover and execute all CRUD operations
- [ ] API responses are consistent and machine-readable

### Dependencies
- M3 (Task CRUD API) - Endpoints must exist before documenting

---

## Dependencies Between Milestones

```
M1 (Backend Foundation)
    |
    v
M2 (JWT Auth)  ------------------+
    |                            |
    v                            v
M3 (Task CRUD) ------------> M4 (Frontend)
    |                            |
    |                            v
    +--------------------> M5 (UI Integration)
                                |
                                v
                        M6 (Agent Integration)
```

---

## Implementation Rules (per Constitution)

1. **Read Specs First**: Before each task, read relevant spec file
2. **Follow Paths**: All endpoints MUST use `/api/{user_id}/tasks`
3. **UUID Mandate**: User IDs are strings, NOT integers
4. **Test Driven**: Write tests before implementation
5. **Verify**: Check acceptance criteria after each task

## Success Criteria

All milestones complete when:
- [ ] All acceptance criteria checked off
- [ ] All tests passing
- [ ] Code reviewed against Constitution
- [ ] Frontend and backend in sync (UUID types match)
- [ ] No violations of Articles I, II, or III

---

## Next Steps

1. Review this plan for accuracy
2. Approve plan to begin implementation
3. Start with Milestone 1, Task 1.1
