# REST API Specification

## Overview

This document defines the REST API endpoints for the Todo App backend. All task endpoints require JWT authentication and MUST include `{user_id}` in the path (Constitution Article I).

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All task endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## API PATHS (Constitution Article I: STRICT PATH COMPLIANCE)

**Approved Endpoints Pattern**: `/api/{user_id}/tasks`

```
GET    /api/{user_id}/tasks              # List user's tasks
GET    /api/{user_id}/tasks/{id}         # Get single task
POST   /api/{user_id}/tasks              # Create task
PUT    /api/{user_id}/tasks/{id}         # Update task
PATCH  /api/{user_id}/tasks/{id}/toggle  # Toggle completion
DELETE /api/{user_id}/tasks/{id}         # Delete task
```

**VIOLATION WARNING**: Using `/tasks` without `{user_id}` is unconstitutional!

---

## Endpoints

### Authentication Endpoints (Global - No user_id in path)

#### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2025-01-01T10:00:00Z"
  }
}
```

**Response Schema (user.id is UUID String)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2025-01-01T10:00:00Z"
}
```

#### POST /auth/login

Authenticate and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### POST /auth/logout

Logout and invalidate the token.

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

### Task Endpoints (Constitution Article I: `/api/{user_id}/tasks`)

#### GET /api/{user_id}/tasks

Retrieve all tasks for the authenticated user.

**Path Parameters:**
- `user_id` (string, required): The user's UUID

**Query Parameters:**
- `completed` (optional): Filter by status (`true` or `false`)
- `search` (optional): Search term for title/description

**Response (200 OK):**
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Note**: `user_id` in response is a UUID String (Constitution Article III)

---

#### GET /api/{user_id}/tasks/{id}

Retrieve a single task by ID.

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Response (200 OK):** Full task object with UUID user_id

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

#### POST /api/{user_id}/tasks

Create a new task for the specified user.

**Path Parameters:**
- `user_id` (string, required): The user's UUID

**Request:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

**Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

#### PUT /api/{user_id}/tasks/{id}

Update an existing task.

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Request:**
```json
{
  "title": "Buy groceries and snacks",
  "description": "Updated description"
}
```

**Response (200 OK):** Updated task object with UUID user_id

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

#### PATCH /api/{user_id}/tasks/{id}/toggle

Toggle task completion status.

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Response (200 OK):** Updated task object with toggled completed status

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

#### DELETE /api/{user_id}/tasks/{id}

Delete a task.

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Response (204 No Content):** No body

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

## HTTP Methods Summary (Article I Compliant)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/auth/register` | Create account | {email, password} |
| POST | `/auth/login` | Get token | {email, password} |
| POST | `/auth/logout` | End session | - |
| GET | `/api/{user_id}/tasks` | List tasks | - |
| GET | `/api/{user_id}/tasks/{id}` | Get task | - |
| POST | `/api/{user_id}/tasks` | Create task | {title, description?} |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | {title?, description?, completed?} |
| PATCH | `/api/{user_id}/tasks/{id}/toggle` | Toggle status | - |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | - |

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Accessing another user's resource |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

---

## CONSTITUTION COMPLIANCE VERIFICATION

| Requirement | Status | Notes |
|-------------|--------|-------|
| Article I: `{user_id}` in path | ✅ VERIFIED | All task endpoints use `/api/{user_id}/tasks` |
| Article II: SQLModel | ✅ VERIFIED | Backend uses SQLModel |
| Article III: UUID user_id | ✅ VERIFIED | user_id is String/UUID in all layers |
| Article III: UUID in response | ✅ VERIFIED | Response includes UUID user_id |

---

## Response Headers

```
Content-Type: application/json
Authorization: Bearer <token>  (on successful auth)
```

## Rate Limiting

- 60 requests per minute for authenticated endpoints
- 20 requests per minute for auth endpoints
