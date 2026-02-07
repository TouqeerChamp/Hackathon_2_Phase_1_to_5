"""
Storage Manager for the Todo App.

This module provides the StorageManager class which handles saving and loading
tasks to/from a JSON file for persistence.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from src.models.task import Task


class StorageManager:
    """
    Manages task persistence using JSON files.
    
    The StorageManager handles saving and loading tasks to/from a JSON file,
    ensuring data persists between application runs.
    """
    
    def __init__(self, file_path: str = "data/tasks.json"):
        """
        Initialize the StorageManager with a file path.
        
        Args:
            file_path: Path to the JSON file for storing tasks
        """
        self.file_path = Path(file_path)
        # Create the data directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_tasks(self, tasks: Dict[int, Task]) -> None:
        """
        Save tasks to the JSON file.
        
        Args:
            tasks: Dictionary of tasks to save, with ID as key and Task as value
        """
        # Convert tasks to a serializable format
        tasks_data = {}
        for task_id, task in tasks.items():
            tasks_data[task_id] = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'completed': task.completed
            }
        
        # Write to file
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(tasks_data, file, indent=2)
    
    def load_tasks(self) -> Dict[int, Task]:
        """
        Load tasks from the JSON file.
        
        Returns:
            Dictionary of tasks with ID as key and Task as value
        """
        if not self.file_path.exists():
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                tasks_data = json.load(file)
            
            tasks = {}
            for task_id_str, task_data in tasks_data.items():
                task_id = int(task_id_str)
                task = Task(
                    id=task_data['id'],
                    title=task_data['title'],
                    description=task_data['description'],
                    completed=task_data['completed']
                )
                tasks[task_id] = task
            
            return tasks
        except (json.JSONDecodeError, KeyError, ValueError):
            # If there's an error loading the file, return empty dict
            return {}
    
    def get_next_id(self) -> int:
        """
        Determine the next available ID based on the loaded tasks.
        
        Returns:
            The next available task ID
        """
        if not self.file_path.exists():
            return 1
        
        tasks = self.load_tasks()
        if not tasks:
            return 1
        
        return max(tasks.keys()) + 1