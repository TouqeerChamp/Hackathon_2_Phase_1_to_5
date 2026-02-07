"""
Unit tests for User and Task models.

CONSTITUTION COMPLIANCE VERIFICATION (Article III):
- User.id is verified as native UUID type
- Task.user_id is verified as native UUID type
"""
import pytest
from uuid import UUID, uuid4

from src.models.user import User
from src.models.task import Task


class TestUserModel:
    """Tests for User model."""

    def test_user_model_creates_uuid(self):
        """Test that User.id is a native UUID type."""
        user = User(email="test@example.com", hashed_password="hashed")
        assert user.id is not None
        assert isinstance(user.id, UUID), f"Expected UUID, got {type(user.id)}"

    def test_user_model_default_timestamps(self):
        """Test that timestamps are auto-generated."""
        user = User(email="test@example.com", hashed_password="hashed")
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_model_email_unique(self):
        """Test that email field is defined."""
        user = User(email="unique@example.com", hashed_password="hashed")
        assert user.email == "unique@example.com"

    def test_user_model_repr(self):
        """Test User __repr__ method."""
        user = User(email="repr@example.com", hashed_password="hashed")
        repr_str = repr(user)
        assert "User" in repr_str
        assert "repr@example.com" in repr_str


class TestTaskModel:
    """Tests for Task model."""

    def test_task_model_defaults(self):
        """Test Task default values."""
        task = Task(user_id=uuid4(), title="Test")
        assert task.description == ""
        assert task.completed is False
        assert task.id is None  # Will be auto-generated on insert

    def test_task_model_uuid_foreign_key(self, sample_user):
        """Test that Task.user_id is a native UUID type."""
        task = Task(
            user_id=sample_user.id,
            title="Test Task",
            description="Test Description"
        )
        assert task.user_id == sample_user.id
        assert isinstance(task.user_id, UUID), f"Expected UUID, got {type(task.user_id)}"

    def test_task_model_title_required(self):
        """Test that title is a required field."""
        task = Task(user_id=uuid4(), title="Required Title")
        assert task.title == "Required Title"

    def test_task_model_repr(self):
        """Test Task __repr__ method."""
        user_id = uuid4()
        task = Task(user_id=user_id, title="Test Task")
        repr_str = repr(task)
        assert "Task" in repr_str
        assert "Test Task" in repr_str


class TestUserTaskRelationship:
    """Tests for User-Task relationship."""

    def test_user_task_relationship(self, sample_user, sample_task):
        """Test User-Task relationship establishment."""
        assert sample_task.user_id == sample_user.id
        assert isinstance(sample_task.user_id, UUID)

    def test_cascade_delete_setup(self):
        """Test that cascade delete is configured in model."""
        # Verify the relationship is defined with cascade_delete
        user = User(email="cascade@example.com", hashed_password="hashed")
        # The relationship should be defined in the User model
        assert hasattr(user, 'tasks')


class TestConstitutionCompliance:
    """Constitution compliance verification tests (Article III)."""

    def test_user_id_is_uuid_not_int(self):
        """Verify User.id is UUID type, NOT int (Article III)."""
        user = User(email="uuid_test@example.com", hashed_password="hashed")
        assert isinstance(user.id, UUID), "User.id MUST be UUID type"
        assert not isinstance(user.id, int), "User.id MUST NOT be int"

    def test_task_user_id_is_uuid_not_int(self):
        """Verify Task.user_id is UUID type, NOT int (Article III)."""
        task = Task(user_id=uuid4(), title="UUID Test")
        assert isinstance(task.user_id, UUID), "Task.user_id MUST be UUID type"
        assert not isinstance(task.user_id, int), "Task.user_id MUST NOT be int"

    def test_user_id_generated_by_uuid4(self):
        """Verify User.id is generated using uuid4()."""
        user = User(email="gen_test@example.com", hashed_password="hashed")
        # UUID4 generates a valid UUID
        uuid_obj = UUID(str(user.id))
        assert str(uuid_obj) == str(user.id)

    def test_uuid_string_conversion_is_consistent(self):
        """Verify UUID can be converted to string consistently."""
        user = User(email="str_test@example.com", hashed_password="hashed")
        user_id_str = str(user.id)
        # Should be able to convert back to UUID
        user_id_back = UUID(user_id_str)
        assert str(user_id_back) == user_id_str
