# API Contracts: Todo App Features

## Task Management Endpoints

### Add Task
- **Command**: `add [title]` or `add [title] [description]`
- **Input**: Title (required string), Description (optional string)
- **Output**: Task object with ID, Title, Description, and Completion status
- **Success**: Returns the created task with a unique ID
- **Error**: Returns error message if title is empty

### View All Tasks
- **Command**: `list` or `list tasks`
- **Input**: None
- **Output**: Array of Task objects
- **Success**: Returns all tasks in the system
- **Error**: Returns message if no tasks exist

### Get Task by ID
- **Command**: Internal operation for other functions
- **Input**: Task ID (integer)
- **Output**: Single Task object
- **Success**: Returns the requested task
- **Error**: Returns error if task doesn't exist

### Update Task
- **Command**: `update [id] [new title]` or `update [id] [new title] [new description]`
- **Input**: Task ID (integer), new title (optional string), new description (optional string)
- **Output**: Updated Task object
- **Success**: Returns the updated task
- **Error**: Returns error if task doesn't exist

### Delete Task
- **Command**: `delete [id]` or `remove [id]`
- **Input**: Task ID (integer)
- **Output**: Boolean success indicator
- **Success**: Returns true if task was deleted
- **Error**: Returns error if task doesn't exist

### Toggle Task Completion
- **Command**: `done [id]` or `complete [id]`
- **Input**: Task ID (integer)
- **Output**: Updated Task object
- **Success**: Returns the task with flipped completion status
- **Error**: Returns error if task doesn't exist

## Natural Language Agent Contract

### Parse Command
- **Input**: Natural language command string
- **Output**: Parsed command object with action type and parameters
- **Success**: Returns recognized action and extracted parameters
- **Error**: Returns error if command is not recognized

### Execute Command
- **Input**: Parsed command object
- **Output**: Result of command execution
- **Success**: Returns appropriate result based on command type
- **Error**: Returns error message if execution fails