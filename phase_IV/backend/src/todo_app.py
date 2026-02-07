"""
Main entry point for the Todo App.

This module initializes the application components and starts the main loop.
"""
from src.services.task_manager import TaskManager
from src.services.storage_manager import StorageManager
from src.agent.todo_agent import TodoAgent
from src.ui.cli_interface import CLIInterface


def main():
    """
    Main entry point for the Todo App.
    
    Initializes all required components and starts the CLI interface.
    """
    print("Initializing Todo App...")
    
    # Initialize the storage manager
    storage_manager = StorageManager("data/tasks.json")
    
    # Initialize the task manager with storage
    task_manager = TaskManager(storage_manager)
    
    # Initialize the todo agent with the task manager
    todo_agent = TodoAgent(task_manager)
    
    # Initialize the CLI interface with both components
    cli_interface = CLIInterface(task_manager, todo_agent)
    
    print("Todo App initialized successfully!")
    print(f"Loaded {len(task_manager.get_all_tasks())} tasks from storage.")
    
    # Start the main application loop
    cli_interface.run()


if __name__ == "__main__":
    main()