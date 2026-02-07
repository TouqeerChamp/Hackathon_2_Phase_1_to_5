"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
from sqlmodel import SQLModel, create_engine
from src.models.user import User
from src.models.task import Task

# Use SQLite for testing (note: SQLite stores UUID as TEXT)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    yield engine


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a database session for each test."""
    from sqlmodel import Session
    SQLModel.metadata.create_all(engine)
    with Session(bind=engine) as session:
        yield session
        session.rollback()
        # Clean up test data
        session.query(Task).delete()
        session.query(User).delete()
        session.commit()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    from src.models.user import User
    user = User(email="test@example.com", hashed_password="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_task(db_session, sample_user):
    """Create a sample task for testing."""
    from src.models.task import Task
    task = Task(
        user_id=sample_user.id,
        title="Test Task",
        description="Test Description"
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task
