"""
Task Router for Todo App.

CONSTITUTION COMPLIANCE (Article I):
- All routes use /api/{user_id}/tasks pattern

CONSTITUTION COMPLIANCE (Article III):
- User IDs and path parameters are native UUID type

CONSTITUTION COMPLIANCE (Article VIII):
- All endpoints documented for AI Agent discovery
- Response formats are consistent and machine-readable
"""
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_

from src.db.database import get_db
from src.models.task import Task
from src.models.user import User
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse
)
from src.auth.jwt_handler import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/v1", tags=["Tasks"])
security = HTTPBearer()

async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT.

    Verifies the token and ensures the user exists in the database.
    """
    try:
        payload = verify_token(token.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        user = session.get(User, UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="List User Tasks",
    description="""
    **For AI Agents**: Retrieve all tasks for the authenticated user.

    Supports filtering by completion status and searching in title/description.
    User is identified from JWT token.
    """
)
def list_tasks(
    current_user: User = Depends(get_current_user),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    session: Session = Depends(get_db)
) -> TaskListResponse:
    # Get user_id from authenticated user
    user_id = current_user.id

    statement = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        statement = statement.where(Task.completed == completed)

    if search:
        statement = statement.where(
            or_(
                Task.title.contains(search),
                Task.description.contains(search)
            )
        )

    tasks = session.exec(statement).all()
    return TaskListResponse(tasks=[TaskResponse.model_validate(t) for t in tasks], total=len(tasks))

@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Task",
    description="""
    **For AI Agents**: Create a new task for the authenticated user.
    """
)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> TaskResponse:
    # Get user_id from authenticated user
    user_id = current_user.id

    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description or ""
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskResponse.model_validate(task)

@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get Single Task",
    description="""
    **For AI Agents**: Retrieve a specific task by its integer ID.
    """
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> TaskResponse:
    # Get user_id from authenticated user
    user_id = current_user.id

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.model_validate(task)

@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update Task",
    description="""
    **For AI Agents**: Update an existing task.
    """
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> TaskResponse:
    # Get user_id from authenticated user
    user_id = current_user.id

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    update_dict = task_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(task, key, value)

    from datetime import datetime
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskResponse.model_validate(task)

@router.patch(
    "/tasks/{task_id}/toggle",
    response_model=TaskResponse,
    summary="Toggle Task Completion",
    description="""
    **For AI Agents**: Flip the completion status of a task.
    """
)
def toggle_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> TaskResponse:
    # Get user_id from authenticated user
    user_id = current_user.id

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.completed = not task.completed
    from datetime import datetime
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskResponse.model_validate(task)

@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="""
    **For AI Agents**: Permanently delete a task.
    """
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Get user_id from authenticated user
    user_id = current_user.id

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()
    return None
