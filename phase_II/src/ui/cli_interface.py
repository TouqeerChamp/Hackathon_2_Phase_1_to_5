"""
CLI Interface for the Todo App.

This module provides the CLIInterface class which handles user interaction
through a console menu system.
"""
from typing import Optional
from src.services.task_manager import TaskManager
from src.agent.todo_agent import TodoAgent


class CLIInterface:
    """
    Handles user interaction through a console menu system.
    
    The CLIInterface provides a user-friendly menu that allows users to
    interact with the todo app using various options.
    """
    
    def __init__(self, task_manager: TaskManager, todo_agent: TodoAgent):
        """
        Initialize the CLIInterface with TaskManager and TodoAgent.
        
        Args:
            task_manager: The TaskManager instance to interact with
            todo_agent: The TodoAgent instance for natural language commands
        """
        self.task_manager = task_manager
        self.todo_agent = todo_agent
    
    def display_menu(self) -> None:
        """Display the main menu options to the user."""
        print("\n" + "="*50)
        print("           TODO APP MENU")
        print("="*50)
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Mark Task Complete/Incomplete")
        print("4. Update Task")
        print("5. Delete Task")
        print("6. Talk to AI Agent (Natural Language Mode)")
        print("7. Exit")
        print("="*50)
    
    def get_user_choice(self) -> str:
        """
        Get the user's menu choice.
        
        Returns:
            The user's choice as a string
        """
        try:
            choice = input("Enter your choice (1-7): ").strip()
            return choice
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting application...")
            return "7"  # Return exit choice
    
    def handle_add_task(self) -> None:
        """Handle the add task option."""
        print("\n--- Add New Task ---")
        title = input("Enter task title: ").strip()
        
        if not title:
            print("Error: Task title cannot be empty.")
            return
        
        description = input("Enter task description (optional): ").strip()
        
        try:
            task = self.task_manager.add_task(title, description)
            print(f"✓ Task added successfully with ID {task.id}")
        except ValueError as e:
            print(f"Error: {e}")
    
    def handle_view_tasks(self) -> None:
        """Handle the view tasks option."""
        print("\n--- All Tasks ---")
        tasks = self.task_manager.get_all_tasks()
        
        if not tasks:
            print("No tasks found.")
            return
        
        for task in tasks:
            status = "✓" if task.completed else "○"
            print(f"[{status}] ID: {task.id} | Title: {task.title}")
            if task.description:
                print(f"    Description: {task.description}")
            print("-" * 40)
    
    def handle_toggle_task(self) -> None:
        """Handle the toggle task completion option."""
        print("\n--- Mark Task Complete/Incomplete ---")
        
        try:
            task_id = int(input("Enter task ID: "))
        except ValueError:
            print("Error: Please enter a valid task ID (number).")
            return
        
        task = self.task_manager.toggle_task_completion(task_id)
        if task:
            status = "completed" if task.completed else "marked incomplete"
            print(f"✓ Task {task_id} {status}.")
        else:
            print(f"✗ Task with ID {task_id} not found.")
    
    def handle_update_task(self) -> None:
        """Handle the update task option."""
        print("\n--- Update Task ---")
        
        try:
            task_id = int(input("Enter task ID: "))
        except ValueError:
            print("Error: Please enter a valid task ID (number).")
            return
        
        # Check if task exists
        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            print(f"✗ Task with ID {task_id} not found.")
            return
        
        print(f"Current title: {task.title}")
        if task.description:
            print(f"Current description: {task.description}")
        
        new_title = input("Enter new title (or press Enter to keep current): ").strip()
        new_description = input("Enter new description (or press Enter to keep current): ").strip()
        
        # Only update if new values were provided
        update_title = new_title if new_title else None
        update_description = new_description if new_description else None
        
        updated_task = self.task_manager.update_task(
            task_id, 
            title=update_title if update_title else None,
            description=update_description if update_description else None
        )
        
        if updated_task:
            print(f"✓ Task {task_id} updated successfully.")
        else:
            print(f"✗ Failed to update task {task_id}.")
    
    def handle_delete_task(self) -> None:
        """Handle the delete task option."""
        print("\n--- Delete Task ---")
        
        try:
            task_id = int(input("Enter task ID: "))
        except ValueError:
            print("Error: Please enter a valid task ID (number).")
            return
        
        success = self.task_manager.delete_task(task_id)
        if success:
            print(f"✓ Task {task_id} deleted successfully.")
        else:
            print(f"✗ Task with ID {task_id} not found.")
    
    def handle_natural_language_mode(self) -> None:
        """Handle the natural language agent interaction."""
        print("\n--- AI Agent Mode ---")
        print("You can now interact with the AI agent using natural language.")
        print("Examples: 'add Buy milk', 'list tasks', 'done 1', 'remove 2'")
        print("Type 'exit' to return to the main menu.\n")
        
        while True:
            try:
                command = input("AI Agent > ").strip()
                
                if command.lower() in ['exit', 'quit', 'back']:
                    break
                
                if not command:
                    print("Please enter a command or 'exit' to return to the main menu.")
                    continue
                
                response = self.todo_agent.execute_command(command)
                print(response)
                
            except (EOFError, KeyboardInterrupt):
                print("\nReturning to main menu...")
                break
    
    def run(self) -> None:
        """Run the main application loop."""
        print("Welcome to the Todo App!")
        
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            
            if choice == "1":
                self.handle_add_task()
            elif choice == "2":
                self.handle_view_tasks()
            elif choice == "3":
                self.handle_toggle_task()
            elif choice == "4":
                self.handle_update_task()
            elif choice == "5":
                self.handle_delete_task()
            elif choice == "6":
                self.handle_natural_language_mode()
            elif choice == "7":
                print("\nThank you for using the Todo App. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 7.")
            
            # Pause to let user see the result before showing menu again
            if choice != "7":
                input("\nPress Enter to continue...")