from typing import List, Optional
from sqlmodel import Session, select
from src.models.task import Task
from src.models.user import User

class DbTaskManager:
    """
    Adapter to allow TodoAgent to interact with the database.
    """
    def __init__(self, session: Session, user: User):
        self.session = session
        self.user = user

    def add_task(self, title: str, description: str = "") -> Task:
        task = Task(title=title, description=description, user_id=self.user.id)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_all_tasks(self) -> List[Task]:
        return self.session.exec(select(Task).where(Task.user_id == self.user.id)).all()

    def toggle_task_completion(self, task_id: int) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        # Verify ownership
        if not task or task.user_id != self.user.id:
            return None
        task.completed = not task.completed
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.session.get(Task, task_id)
        # Verify ownership
        if not task or task.user_id != self.user.id:
            return False
        self.session.delete(task)
        self.session.commit()
        return True

    def update_task(self, task_id: int, title: str = None) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        # Verify ownership
        if not task or task.user_id != self.user.id:
            return None
        if title:
            task.title = title
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
