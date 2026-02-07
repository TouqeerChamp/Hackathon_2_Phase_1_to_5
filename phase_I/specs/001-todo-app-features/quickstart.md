# Quickstart Guide: Todo App Features

## Getting Started

This guide will help you get up and running with the Hackathon II Phase I In-Memory Console Todo App.

### Prerequisites

- Python 3.8 or higher
- WSL environment (if using Windows)
- No external libraries required (pure Python standard library)

### Installation

1. Clone or download the project repository
2. Navigate to the project directory
3. The application is ready to run with no additional setup required

### Running the Application

To start the Todo App, run the following command from the project root:

```bash
python src/todo_app.py
```

### Basic Usage

Once the application starts, you'll see a menu with options to interact with your tasks:

```
Todo App Menu:
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Natural Language Agent
7. Exit
```

### Natural Language Agent Commands

The app includes an intelligent agent that understands natural language commands:

- `add [task title]` - Add a new task (e.g., "add buy groceries")
- `add [task title] [description]` - Add a task with description (e.g., "add call mom call her about dinner")
- `list` or `list tasks` - View all tasks
- `done [id]` or `complete [id]` - Mark a task as complete (e.g., "done 1")
- `remove [id]` or `delete [id]` - Delete a task (e.g., "remove 2")
- `update [id] [new title]` - Update a task title (e.g., "update 1 new task title")

### Example Workflow

1. Start the application: `python src/todo_app.py`
2. Add a task: Select option 1 or use agent command "add buy milk"
3. View tasks: Select option 2 or use agent command "list"
4. Mark complete: Select option 5 or use agent command "done 1"
5. Exit: Select option 7

### Development

To run the unit tests:

```bash
python -m unittest discover tests/
```

### Architecture Overview

The application follows a modular architecture:

- `src/models/task.py` - Task data model
- `src/services/task_manager.py` - Core business logic
- `src/services/storage_manager.py` - In-memory storage with JSON persistence
- `src/agent/todo_agent.py` - Natural language processing agent
- `src/ui/cli_interface.py` - User interface
- `src/todo_app.py` - Main application entry point