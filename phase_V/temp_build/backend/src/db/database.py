"""
Database engine and session management for SQLModel.

This module provides:
- Database engine configuration with connection pooling
- Dependency injection for database sessions
- Table creation utility

IMPORTANT: Uses pool_pre_ping=True for Neon Serverless compatibility
to avoid 'connection closed' errors during idle periods.
"""
from contextlib import contextmanager
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from src.config import get_settings

# Load settings
settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

# Create SQLModel engine with connection pooling
# pool_pre_ping=True: Verifies connection before use (critical for Neon Serverless)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Essential for Neon Serverless - prevents "connection closed" errors
    pool_size=5,  # Base pool size
    max_overflow=10,  # Additional connections when pool is exhausted
    pool_recycle=3600,  # Recycle connections after 1 hour (Neon requirement)
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Yields a session that automatically closes after use.

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    with Session(bind=engine) as session:
        try:
            yield session
        finally:
            session.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Alternative to get_db() for non-FastAPI contexts.

    Usage:
        with get_db_context() as db:
            db.add(user)
            db.commit()
    """
    with Session(bind=engine) as session:
        try:
            yield session
        finally:
            session.close()


def create_db_and_tables() -> None:
    """
    Create all database tables defined in SQLModel metadata.

    This function is called on application startup to ensure
    all tables exist before the first request.

    Tables created:
    - app_users (User model)
    - app_tasks (Task model)
    """
    SQLModel.metadata.create_all(engine)


def drop_db_tables() -> None:
    """
    Drop all database tables defined in SQLModel metadata.

    WARNING: This is destructive and should only be used
    in testing or development environments.
    """
    SQLModel.metadata.drop_all(engine)


def get_engine():
    """
    Get the database engine instance.

    Returns:
        SQLModel engine instance
    """
    return engine
