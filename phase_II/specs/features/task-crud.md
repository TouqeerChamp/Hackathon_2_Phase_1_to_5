# Task CRUD Feature Specification

## Overview

This document defines the Task CRUD feature for the web-based Todo App. The feature enables users to create, read, update, and delete tasks through both the REST API and the web interface.

**Constitution Compliance**:
- Article I: All endpoints use `/api/{user_id}/tasks` pattern
- Article III: User IDs are UUID Strings

## User Stories

| As a... | I want to... | So that... |
|---------|--------------|------------|
| User | Add a new task with title and optional description | I can track things I need to do |
| User | View all my tasks | I can see what I have pending |
| User | View a single task details | I can see the full information |
| User | Update task title and/or description | I can correct or refine my tasks |
| User | Toggle task completion status | I can mark tasks as done or undone |
| User | Delete a task | I can remove no longer needed tasks |

## Data Model (Phase II - Constitution Article III Compliant)

```
Task {
  id: int (positive, auto-generated)
  user_id: str (UUID, foreign key to User)
  title: string (non-empty, trimmed)
  description: string (optional, default: "")
  completed: boolean (default: false)
  created_at: datetime (auto-generated)
  updated_at: datetime (auto-updated)
}
```

**Note**: `user_id` is a UUID String, NOT an integer (per Constitution Article III)

## API Paths (Constitution Article I: STRICT PATH COMPLIANCE)

All endpoints MUST include `{user_id}` in the path:

```
POST   /api/{user_id}/tasks              # Create task
GET    /api/{user_id}/tasks              # List tasks
GET    /api/{user_id}/tasks/{id}         # Get single task
PUT    /api/{user_id}/tasks/{id}         # Update task
PATCH  /api/{user_id}/tasks/{id}/toggle  # Toggle completion
DELETE /api/{user_id}/tasks/{id}         # Delete task
```

---

## Operations

### Create Task (POST /api/{user_id}/tasks)

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

**Validation Rules:**
- `title`: Required, 1-200 characters, trimmed
- `description`: Optional, 0-1000 characters, trimmed
- `user_id`: Must be a valid UUID

---

### Read All Tasks (GET /api/{user_id}/tasks)

**Path Parameters:**
- `user_id` (string, required): The user's UUID

**Query Parameters:**
- `completed` (optional): Filter by completion status
- `search` (optional): Search in title and description

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

### Read Single Task (GET /api/{user_id}/tasks/{id})

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Response (200 OK):** Full task object with UUID user_id

**Error (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

### Update Task (PUT /api/{user_id}/tasks/{id})

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Request:**
```json
{
  "title": "Buy groceries and snacks",
  "completed": true
}
```

**Response (200 OK):** Updated task object

**Validation Rules:**
- At least one field (title, description, completed) must be provided
- Empty string for title is not allowed
- completed is optional

---

### Toggle Completion (PATCH /api/{user_id}/tasks/{id}/toggle)

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Response (200 OK):** Updated task object with toggled completed status

---

### Delete Task (DELETE /api/{user_id}/tasks/{id})

**Path Parameters:**
- `user_id` (string): The user's UUID
- `id` (integer): The task ID

**Response (204 No Content):** No body

**Error (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

---

## UI Requirements

### Task List View
- Display all tasks in a card or list format
- Show completion status with visual indicator (checkbox/strikethrough)
- Include title and truncated description
- Provide action buttons: Edit, Toggle, Delete
- Show task count (total/pending/completed)
- User context managed via UUID from auth session

### Task Creation
- Form with title field (required) and description textarea (optional)
- Submit button
- Validation feedback for empty title
- Task created for authenticated user's UUID

### Task Editing
- Modal or inline edit form
- Pre-populate with current values
- Cancel and Save buttons
- Validation feedback
- Verify task belongs to current user (UUID match)

### Task Deletion
- Confirmation dialog before deletion
- Delete button visible on task card
- Verify task belongs to current user (UUID match)

---

## Business Logic (Phase II - Constitution Compliant)

1. **Auto-incrementing IDs**: Each user's tasks have independent ID sequences (task IDs are integers)
2. **UUID User Identification**: User IDs are UUID strings throughout (Article III)
3. **Validation**: All task titles must be non-empty after trimming
4. **Persistence**: All changes are immediately persisted to the database
5. **User Isolation**: Users can only access their own tasks (by UUID)
6. **Path Compliance**: All endpoints include `{user_id}` (Article I)

---

## Error Handling

| Status Code | Condition |
|-------------|-----------|
| 401 | Missing or invalid JWT token |
| 403 | User trying to access another user's task (UUID mismatch) |
| 404 | Task not found |
| 422 | Validation error (invalid input) |
| 500 | Internal server error |

---

## CONSTITUTION COMPLIANCE CHECKLIST

| Requirement | Status | Notes |
|-------------|--------|-------|
| Article I: `{user_id}` in all paths | ✅ VERIFIED | All 6 CRUD endpoints include user_id |
| Article III: user_id is UUID String | ✅ VERIFIED | Database, API, and responses use UUID |
| Article II: SQLModel ORM | ✅ VERIFIED | Backend uses SQLModel |
| User Isolation | ✅ VERIFIED | Users can only access their own tasks by UUID |
