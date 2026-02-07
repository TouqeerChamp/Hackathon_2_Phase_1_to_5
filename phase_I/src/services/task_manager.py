"""
Task Manager for the Todo App.

This module provides the TaskManager class which handles all CRUD operations
for tasks in memory.
"""
from typing import Dict, List, Optional
from src.models.task import Task
from src.services.storage_manager import StorageManager


class TaskManager:
    """
    Manages tasks in memory with CRUD operations.

    The TaskManager handles all operations related to tasks including
    adding, retrieving, updating, deleting, and toggling completion status.
    """

    def __init__(self, storage_manager: StorageManager = None):
        """
        Initialize the TaskManager with an empty task storage.

        Args:
            storage_manager: Optional StorageManager for persistence
        """
        self.storage_manager = storage_manager or StorageManager()

        # Load existing tasks if available
        self._tasks = self.storage_manager.load_tasks()

        # Determine the next ID based on loaded tasks
        if self._tasks:
            self._next_id = max(self._tasks.keys()) + 1
        else:
            self._next_id = 1
    
    def add_task(self, title: str, description: str = "") -> Task:
        """
        Add a new task to the collection.

        Args:
            title: The title of the task
            description: Optional description of the task

        Returns:
            The newly created Task object with a unique ID

        Raises:
            ValueError: If title is empty or invalid
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        task_id = self._next_id
        self._next_id += 1

        task = Task(id=task_id, title=title.strip(), description=description.strip())
        self._tasks[task_id] = task

        # Save tasks to storage
        self.storage_manager.save_tasks(self._tasks)

        return task
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            The Task object if found, None otherwise
        """
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks in the collection.
        
        Returns:
            A list of all Task objects
        """
        return list(self._tasks.values())
    
    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None) -> Optional[Task]:
        """
        Update an existing task's title and/or description.

        Args:
            task_id: The ID of the task to update
            title: New title for the task (optional)
            description: New description for the task (optional)

        Returns:
            The updated Task object if successful, None if task doesn't exist
        """
        if task_id not in self._tasks:
            return None

        task = self._tasks[task_id]

        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip()

        # Save tasks to storage
        self.storage_manager.save_tasks(self._tasks)

        return task
    
    def toggle_task_completion(self, task_id: int) -> Optional[Task]:
        """
        Toggle the completion status of a task.

        Args:
            task_id: The ID of the task to toggle

        Returns:
            The updated Task object if successful, None if task doesn't exist
        """
        if task_id not in self._tasks:
            return None

        task = self._tasks[task_id]
        task.completed = not task.completed

        # Save tasks to storage
        self.storage_manager.save_tasks(self._tasks)

        return task
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task from the collection.

        Args:
            task_id: The ID of the task to delete

        Returns:
            True if the task was deleted, False if it didn't exist
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]

        # Save tasks to storage
        self.storage_manager.save_tasks(self._tasks)

        return True
    
    def get_next_id(self) -> int:
        """
        Get the next available task ID without incrementing the counter.
        
        Returns:
            The next available task ID
        """
        return self._next_id