"""
Unit tests for Task CRUD operations.

CONSTITUTION COMPLIANCE VERIFICATION:
- Article I: Endpoints follow /api/{user_id}/tasks pattern
- Article III: User IDs and path parameters are native UUID type
- Article VIII: Endpoints have detailed documentation and tags for Agent discovery
"""
import pytest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from fastapi import status
from src.main import app
from src.auth.jwt_handler import create_access_token
from src.models.user import User
from src.models.task import Task
from sqlmodel import Session

client = TestClient(app)

@pytest.fixture
def auth_header(sample_user):
    """Generate auth header for sample user."""
    token = create_access_token(sample_user.id, sample_user.email)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_user(db_session):
    """Create another user to test isolation."""
    user = User(email="other@example.com", hashed_password="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def other_auth_header(other_user):
    """Generate auth header for other user."""
    token = create_access_token(other_user.id, other_user.email)
    return {"Authorization": f"Bearer {token}"}

class TestTaskCRUD:
    """Test suite for Task CRUD operations."""

    def test_create_task(self, sample_user, auth_header):
        """Test creating a new task."""
        data = {
            "title": "New Task",
            "description": "New Task Description"
        }
        response = client.post(
            f"/api/{sample_user.id}/tasks",
            json=data,
            headers=auth_header
        )
        assert response.status_code == status.HTTP_201_CREATED
        res_data = response.json()
        assert res_data["title"] == data["title"]
        assert res_data["description"] == data["description"]
        assert res_data["user_id"] == str(sample_user.id)
        assert res_data["completed"] is False

    def test_list_tasks(self, sample_user, sample_task, auth_header):
        """Test listing user tasks."""
        response = client.get(
            f"/api/{sample_user.id}/tasks",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tasks" in data
        assert data["total"] >= 1
        assert any(t["id"] == sample_task.id for t in data["tasks"])

    def test_get_task(self, sample_user, sample_task, auth_header):
        """Test getting a specific task."""
        response = client.get(
            f"/api/{sample_user.id}/tasks/{sample_task.id}",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == sample_task.title

    def test_update_task(self, sample_user, sample_task, auth_header):
        """Test updating a task."""
        data = {
            "title": "Updated Title",
            "completed": True
        }
        response = client.put(
            f"/api/{sample_user.id}/tasks/{sample_task.id}",
            json=data,
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        res_data = response.json()
        assert res_data["title"] == data["title"]
        assert res_data["completed"] is True

    def test_toggle_task(self, sample_user, sample_task, auth_header):
        """Test toggling task completion."""
        initial_status = sample_task.completed
        response = client.patch(
            f"/api/{sample_user.id}/tasks/{sample_task.id}/toggle",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] == (not initial_status)

    def test_delete_task(self, sample_user, sample_task, auth_header, db_session):
        """Test deleting a task."""
        task_id = sample_task.id
        response = client.delete(
            f"/api/{sample_user.id}/tasks/{task_id}",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Expire session to ensure we fetch from DB
        db_session.expire_all()

        # Verify it's gone
        task_in_db = db_session.get(Task, task_id)
        assert task_in_db is None

    def test_task_isolation(self, sample_user, other_user, sample_task, other_auth_header):
        """Test that user cannot access another user's task."""
        # Other user tries to access sample_user's task
        response = client.get(
            f"/api/{sample_user.id}/tasks/{sample_task.id}",
            headers=other_auth_header
        )
        # Should be forbidden because of path user_id mismatch
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_wrong_path_user_id(self, sample_user, sample_task, auth_header):
        """Test that accessing tasks via wrong path ID is forbidden."""
        fake_uuid = uuid4()
        response = client.get(
            f"/api/{fake_uuid}/tasks/{sample_task.id}",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthorized_access(self, sample_user, sample_task):
        """Test that tasks cannot be accessed without token."""
        response = client.get(f"/api/{sample_user.id}/tasks")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_tasks(self, sample_user, sample_task, auth_header):
        """Test searching tasks."""
        # Search for something that matches
        response = client.get(
            f"/api/{sample_user.id}/tasks?search=Test",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1

        # Search for something that doesn't match
        response = client.get(
            f"/api/{sample_user.id}/tasks?search=NonExistent",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0

    def test_filter_completed(self, sample_user, sample_task, auth_header):
        """Test filtering tasks by completion status."""
        # Initially false
        response = client.get(
            f"/api/{sample_user.id}/tasks?completed=false",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1

        response = client.get(
            f"/api/{sample_user.id}/tasks?completed=true",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
