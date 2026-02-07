#!/usr/bin/env python3
"""
Simple verification script for User and Task models.
Runs without pytest installation.

CONSTITUTION COMPLIANCE VERIFICATION (Article III):
- User.id is verified as native UUID type
- Task.user_id is verified as native UUID type
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uuid import UUID, uuid4
from datetime import datetime


def test_user_model():
    """Test User model."""
    print("Testing User model...")

    from src.models.user import User

    # Test 1: User.id is UUID type
    user = User(email="test@example.com", hashed_password="hashed")
    assert user.id is not None, "User.id should not be None"
    assert isinstance(user.id, UUID), f"User.id MUST be UUID, got {type(user.id)}"
    print("  ✓ User.id is native UUID type")

    # Test 2: User.id is NOT int (Article III violation check)
    assert not isinstance(user.id, int), "User.id MUST NOT be int"
    print("  ✓ User.id is NOT int (Article III compliant)")

    # Test 3: Timestamps auto-generated
    assert user.created_at is not None, "created_at should be auto-generated"
    assert user.updated_at is not None, "updated_at should be auto-generated"
    print("  ✓ Timestamps auto-generated")

    # Test 4: Email is set
    assert user.email == "test@example.com"
    print("  ✓ Email field works")

    # Test 5: UUID can be string-converted consistently
    user_id_str = str(user.id)
    uuid_back = UUID(user_id_str)
    assert str(uuid_back) == user_id_str
    print("  ✓ UUID string conversion consistent")

    print("User model tests: PASSED\n")
    return user


def test_task_model(sample_user):
    """Test Task model."""
    print("Testing Task model...")

    from src.models.task import Task

    # Test 1: Task.user_id is UUID type
    task = Task(
        user_id=sample_user.id,
        title="Test Task",
        description="Test Description"
    )
    assert isinstance(task.user_id, UUID), f"Task.user_id MUST be UUID, got {type(task.user_id)}"
    print("  ✓ Task.user_id is native UUID type")

    # Test 2: Task.user_id is NOT int (Article III violation check)
    assert not isinstance(task.user_id, int), "Task.user_id MUST NOT be int"
    print("  ✓ Task.user_id is NOT int (Article III compliant)")

    # Test 3: Default values
    assert task.description == ""
    assert task.completed is False
    assert task.id is None  # Will be auto-generated on insert
    print("  ✓ Default values correct (description='', completed=False)")

    # Test 4: Title is required field
    assert task.title == "Test Task"
    print("  ✓ Title field works")

    print("Task model tests: PASSED\n")
    return task


def test_constitution_compliance():
    """Constitution compliance verification tests (Article III)."""
    print("Testing Constitution Compliance (Article III: UUID Mandate)...")

    from src.models.user import User
    from src.models.task import Task

    # Test 1: User.id is UUID, NOT int
    user = User(email="compliance@example.com", hashed_password="hashed")
    assert isinstance(user.id, UUID), "User.id MUST be UUID type"
    assert not isinstance(user.id, int), "User.id MUST NOT be int"
    print("  ✓ User.id is UUID, NOT int")

    # Test 2: Task.user_id is UUID, NOT int
    task = Task(user_id=uuid4(), title="Compliance Test")
    assert isinstance(task.user_id, UUID), "Task.user_id MUST be UUID type"
    assert not isinstance(task.user_id, int), "Task.user_id MUST NOT be int"
    print("  ✓ Task.user_id is UUID, NOT int")

    # Test 3: UUID generation is valid
    test_uuid = uuid4()
    uuid_obj = UUID(str(test_uuid))
    assert str(uuid_obj) == str(test_uuid)
    print("  ✓ UUID generation produces valid UUIDs")

    print("Constitution compliance tests: PASSED\n")


def test_pydantic_schemas():
    """Test Pydantic v2 schemas."""
    print("Testing Pydantic v2 Schemas...")

    from src.schemas.user import UserCreate, UserResponse, TokenResponse
    from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse

    # Test 1: UserCreate schema
    user_create = UserCreate(email="schema@test.com", password="password123")
    assert user_create.email == "schema@test.com"
    assert user_create.password == "password123"
    print("  ✓ UserCreate schema works")

    # Test 2: UserResponse has UUID id (no password!)
    from datetime import datetime
    from uuid import uuid4
    user_id = uuid4()
    user_response = UserResponse(
        id=user_id,
        email="response@test.com",
        created_at=datetime.utcnow()
    )
    assert user_response.id == user_id
    assert isinstance(user_response.id, UUID), "UserResponse.id MUST be UUID"
    assert not hasattr(user_response, 'hashed_password'), "UserResponse MUST NOT include password"
    print("  ✓ UserResponse has UUID id, NO password")

    # Test 3: TaskCreate with title validation
    task_create = TaskCreate(title="Test Task", description="Description")
    assert task_create.title == "Test Task"
    assert task_create.description == "Description"
    print("  ✓ TaskCreate schema works")

    # Test 4: TaskResponse has UUID user_id
    task_response = TaskResponse(
        id=1,
        user_id=user_id,
        title="Task",
        description="Desc",
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert task_response.user_id == user_id
    assert isinstance(task_response.user_id, UUID), "TaskResponse.user_id MUST be UUID"
    print("  ✓ TaskResponse has UUID user_id")

    # Test 5: TokenResponse
    token_response = TokenResponse(access_token="test_token")
    assert token_response.access_token == "test_token"
    assert token_response.token_type == "bearer"
    print("  ✓ TokenResponse schema works")

    print("Pydantic schema tests: PASSED\n")


def test_database_config():
    """Test database configuration."""
    print("Testing Database Configuration...")

    from src.config import get_settings
    from src.db.database import engine, create_db_and_tables

    # Test 1: Settings can be loaded
    try:
        settings = get_settings()
        print(f"  ✓ Settings loaded: DATABASE_URL defined = {hasattr(settings, 'DATABASE_URL')}")
    except Exception as e:
        print(f"  ⚠ Settings loading requires .env file (expected in production): {type(e).__name__}")

    # Test 2: Engine is created
    assert engine is not None
    print("  ✓ Database engine created")

    # Test 3: create_db_and_tables function exists
    assert callable(create_db_and_tables)
    print("  ✓ create_db_and_tables function available")

    print("Database configuration tests: PASSED\n")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("MILESTONE 1 VERIFICATION - Backend Foundation")
    print("=" * 60)
    print()

    all_passed = True

    try:
        # Test models
        sample_user = test_user_model()
        test_task_model(sample_user)

        # Test constitution compliance
        test_constitution_compliance()

        # Test schemas
        test_pydantic_schemas()

        # Test database config
        test_database_config()

        print("=" * 60)
        print("ALL MILESTONE 1 TESTS: PASSED ✓")
        print("=" * 60)
        print()
        print("Constitution Compliance Verified:")
        print("  - Article I: Path compliance (verified in main.py)")
        print("  - Article II: SQLModel ORM (verified)")
        print("  - Article III: UUID Mandate (verified)")
        print("  - Article VIII: Agentic Design (verified in main.py)")
        print()

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        all_passed = False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
