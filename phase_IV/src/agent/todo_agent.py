"""
Todo Agent for the Todo App.

This module provides the TodoAgent class which handles natural language
parsing and maps commands to TaskManager methods.
"""
import re
from typing import Tuple, Optional
from src.services.task_manager import TaskManager


class TodoAgent:
    """
    Handles natural language commands for the Todo App.
    
    The TodoAgent parses natural language commands and maps them to
    appropriate TaskManager methods, providing an intelligent interface
    for users to interact with the todo app.
    """
    
    def __init__(self, task_manager: TaskManager):
        """
        Initialize the TodoAgent with a TaskManager.
        
        Args:
            task_manager: The TaskManager instance to interact with
        """
        self.task_manager = task_manager
    
    def parse_command(self, command: str) -> Tuple[str, list]:
        """
        Parse a natural language command and extract action and parameters.
        
        Args:
            command: The natural language command to parse
            
        Returns:
            A tuple containing the action type and a list of parameters
        """
        command = command.strip().lower()
        
        # Pattern for "add [title]" or "add [title] [description]"
        add_pattern = r'^add\s+(.+?)(?:\s+(.+))?$'
        add_match = re.match(add_pattern, command)
        if add_match:
            title = add_match.group(1).strip()
            description = add_match.group(2).strip() if add_match.group(2) else ""
            return "add", [title, description]
        
        # Pattern for "list" or "list tasks"
        if command in ["list", "list tasks"]:
            return "list", []
        
        # Pattern for "done [id]", "complete [id]"
        complete_pattern = r'^(done|complete)\s+(\d+)$'
        complete_match = re.match(complete_pattern, command)
        if complete_match:
            task_id = int(complete_match.group(2))
            return "complete", [task_id]
        
        # Pattern for "remove [id]", "delete [id]"
        delete_pattern = r'^(remove|delete)\s+(\d+)$'
        delete_match = re.match(delete_pattern, command)
        if delete_match:
            task_id = int(delete_match.group(2))
            return "delete", [task_id]
        
        # Pattern for "update [id] [new title]"
        update_pattern = r'^update\s+(\d+)\s+(.+)$'
        update_match = re.match(update_pattern, command)
        if update_match:
            task_id = int(update_match.group(1))
            new_title = update_match.group(2).strip()
            return "update", [task_id, new_title]
        
        # If no pattern matches, return unknown
        return "unknown", [command]
    
    def execute_command(self, command: str) -> str:
        """
        Execute a natural language command and return the result.
        
        Args:
            command: The natural language command to execute
            
        Returns:
            A string response indicating the result of the command execution
        """
        try:
            action, params = self.parse_command(command)
            
            if action == "add":
                title, description = params
                task = self.task_manager.add_task(title, description)
                return f"Task added successfully with ID {task.id}: {task.title}"
            
            elif action == "list":
                tasks = self.task_manager.get_all_tasks()
                if not tasks:
                    return "No tasks found."
                
                task_list = []
                for task in tasks:
                    status = "✓" if task.completed else "○"
                    task_list.append(f"[{status}] {task.id}. {task.title} - {task.description}")
                
                return "\n".join(task_list)
            
            elif action == "complete":
                task_id = params[0]
                task = self.task_manager.toggle_task_completion(task_id)
                if task:
                    status = "completed" if task.completed else "marked incomplete"
                    return f"Task {task_id} {status}."
                else:
                    return f"Task with ID {task_id} not found."
            
            elif action == "delete":
                task_id = params[0]
                success = self.task_manager.delete_task(task_id)
                if success:
                    return f"Task {task_id} deleted successfully."
                else:
                    return f"Task with ID {task_id} not found."
            
            elif action == "update":
                task_id, new_title = params
                updated_task = self.task_manager.update_task(task_id, title=new_title)
                if updated_task:
                    return f"Task {task_id} updated successfully: {updated_task.title}"
                else:
                    return f"Task with ID {task_id} not found."
            
            elif action == "unknown":
                return f"Unknown command: '{command}'. Please try again with a valid command."
            
            else:
                return f"Unsupported action: {action}"
        
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"