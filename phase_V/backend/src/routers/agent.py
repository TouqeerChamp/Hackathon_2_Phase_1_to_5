from typing import Annotated, Dict, Any, List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlmodel import Session, select

from src.db.database import get_db
from src.models.user import User
from src.models.task import Task
from src.routers.tasks import get_current_user
from src.agent.todo_agent import TodoAgent
from src.agent.strategist_agent import StrategistAgent
from src.services.db_task_manager import DbTaskManager

router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])

class AgentPrompt(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    response: str

class AnalysisStats(BaseModel):
    total: int
    completed: int
    pending: int
    completion_rate: float

class AnalysisResponse(BaseModel):
    summary: str
    insights: List[str]
    recommendations: List[str]
    patterns: List[str]
    stats: AnalysisStats

@router.post(
    "/prompt",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Agent Command",
    description="""
    Execute a natural language command using the Todo Agent.

    Supported commands:
    - "add <title> [description]"
    - "list"
    - "complete <id>"
    - "delete <id>"
    - "update <id> <new title>"
    """
)
async def agent_prompt(
    body: AgentPrompt,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    # Initialize the DB adapter
    manager = DbTaskManager(session, user)

    # Initialize the legacy agent with the DB adapter
    # The agent expects a TaskManager-like interface, which our adapter provides
    agent = TodoAgent(manager)

    # Execute
    response_text = agent.execute_command(body.prompt)

    return {"response": response_text}


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze User Tasks",
    description="""
    Analyze the current user's tasks and provide intelligent insights,
    recommendations, and patterns.

    The Strategist Agent examines:
    - Task completion rates
    - Task patterns and themes
    - Pending vs completed tasks
    - Actionable recommendations

    Returns a comprehensive analysis report with statistics and suggestions.
    """
)
async def analyze_tasks(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Analyze user tasks and provide strategic insights.

    This endpoint uses the Strategist Agent to analyze the current user's
    tasks and provide actionable recommendations, insights, and pattern detection.
    """
    # Fetch all tasks for the current user
    statement = select(Task).where(Task.user_id == user.id)
    tasks = session.exec(statement).all()

    # Initialize the Strategist Agent
    strategist = StrategistAgent(list(tasks))

    # Perform analysis
    analysis = strategist.analyze()

    return analysis
