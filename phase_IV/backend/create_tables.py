"""
Script to create all database tables in Neon DB.

This script imports all models and runs create_all to ensure
tables are created without dropping existing data.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.db.database import create_db_and_tables, engine
from src.models import User, Task, Conversation, Message
from sqlmodel import text

def verify_tables():
    """Verify tables exist in the database."""
    from sqlmodel import Session

    with Session(engine) as session:
        # Query PostgreSQL information schema for our tables
        result = session.exec(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE 'app_%'
                ORDER BY table_name;
            """)
        )
        tables = [row[0] for row in result]
        return tables

def main():
    print("Creating database tables...")
    print(f"Models loaded: User, Task, Conversation, Message")

    # Create all tables
    create_db_and_tables()

    print("\nVerifying tables in Neon DB...")
    tables = verify_tables()

    if tables:
        print(f"\nTables found ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
    else:
        print("\nNo tables found with 'app_' prefix!")

    # Check expected tables
    expected = {'app_users', 'app_tasks', 'app_conversations', 'app_messages'}
    found = set(tables)

    if expected.issubset(found):
        print("\n✓ All expected tables exist!")
    else:
        missing = expected - found
        print(f"\n✗ Missing tables: {missing}")

if __name__ == "__main__":
    main()
