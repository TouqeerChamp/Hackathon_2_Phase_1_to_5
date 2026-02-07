"""
Task model for the Todo App.

This module defines the Task dataclass which represents a single todo item.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """
    Represents a single todo item in the application.
    
    Attributes:
        id: Unique identifier for the task (positive integer)
        title: Title or name of the task (non-empty string)
        description: Optional detailed description of the task (default: "")
        completed: Completion status of the task (default: False)
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False

    def __post_init__(self):
        """Validate the Task attributes after initialization."""
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("Task ID must be a positive integer")
        
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Task title must be a non-empty string")
        
        if not isinstance(self.description, str):
            raise ValueError("Task description must be a string")
        
        if not isinstance(self.completed, bool):
            raise ValueError("Task completed status must be a boolean")