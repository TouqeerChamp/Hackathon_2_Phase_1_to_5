"""
Database module for SQLModel integration.

Exports:
- engine: SQLModel database engine
- get_db: Dependency for getting database session
- get_db_context: Context manager for database sessions
- create_db_and_tables: Create all tables
- drop_db_tables: Drop all tables (WARNING: destructive)
"""
from src.db.database import (
    engine,
    get_db,
    get_db_context,
    create_db_and_tables,
    drop_db_tables,
    get_engine,
)

__all__ = [
    "engine",
    "get_db",
    "get_db_context",
    "create_db_and_tables",
    "drop_db_tables",
    "get_engine",
]
