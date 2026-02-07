# Data Model: Todo App Features

## Task Entity

### Definition
The Task entity represents a single todo item in the application.

### Attributes
- **id**: `int` - Unique identifier for the task (auto-generated)
- **title**: `str` - Title or name of the task (required)
- **description**: `str` - Optional detailed description of the task (default: "")
- **completed**: `bool` - Completion status of the task (default: False)

### Dataclass Implementation
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
```

### Validation Rules
- `id` must be a positive integer
- `title` must not be empty or None
- `description` can be empty but not None
- `completed` must be a boolean value

### State Transitions
- A task starts with `completed=False`
- A task can transition from `completed=False` to `completed=True` (mark complete)
- A task can transition from `completed=True` to `completed=False` (mark incomplete)

## TaskManager Data Flow

### Add Task
1. Input: title (str), description (optional str)
2. Process: Create new Task with auto-generated ID
3. Output: Task object with unique ID

### View Tasks
1. Input: None (for all tasks) or ID (for specific task)
2. Process: Retrieve from in-memory storage
3. Output: Task object(s)

### Update Task
1. Input: ID (int), new title (optional str), new description (optional str)
2. Process: Update existing Task object
3. Output: Updated Task object

### Delete Task
1. Input: ID (int)
2. Process: Remove Task from storage
3. Output: Boolean indicating success

### Toggle Completion
1. Input: ID (int)
2. Process: Flip the completed status of Task
3. Output: Updated Task object

## Storage Model

### In-Memory Storage
- Use a Python dictionary with ID as key and Task object as value
- Structure: `{id: Task, ...}`
- Maintain a separate counter for auto-generating IDs

### JSON Persistence (for todo-persistence-expert agent)
- Serialize Task objects to JSON format
- Store as array of task objects
- Maintain the same structure as in-memory for easy conversion