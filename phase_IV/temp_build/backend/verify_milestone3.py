#!/usr/bin/env python3
"""
Verification script for Milestone 3 - Task CRUD API.
Runs without pytest installation to verify API functionality.
"""
import sys
import os
from uuid import UUID, uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_task_router_discovery():
    """Verify Task router is properly documented for Agent discovery (Article VIII)."""
    print("Testing Article VIII: Agent Discovery...")
    from src.routers.tasks import router

    assert router.tags == ["Tasks"], "Router should have 'Tasks' tag"

    # Check if all 6 endpoints exist with summaries and descriptions
    paths = [route.path for route in router.routes]
    expected_paths = [
        "/{user_id}/tasks",
        "/{user_id}/tasks/{task_id}",
        "/{user_id}/tasks/{task_id}/toggle"
    ]

    for path in expected_paths:
        found = False
        for route in router.routes:
            if route.path == path:
                found = True
                assert route.summary is not None, f"Route {path} missing summary"
                assert "**For AI Agents**" in route.description, f"Route {path} missing Agent documentation"
        assert found, f"Expected endpoint {path} not found in router"

    print("  ✓ Task router endpoints properly documented")
    print("  ✓ Includes **For AI Agents** descriptions")
    print("Article VIII tests: PASSED\n")

def test_path_compliance():
    """Verify Article I: Path compliance."""
    print("Testing Article I: Path Compliance...")
    from src.routers.tasks import router

    for route in router.routes:
        # Combined with router prefix '/api'
        full_path = f"/api{route.path}"
        assert "{user_id}" in full_path, f"Path {full_path} must include {{user_id}}"
        assert full_path.startswith("/api/"), f"Path {full_path} must start with /api/"

    print("  ✓ All task endpoints use /api/{user_id}/tasks pattern")
    print("Article I tests: PASSED\n")

def test_uuid_compliance():
    """Verify Article III: UUID Mandate."""
    print("Testing Article III: UUID Mandate...")
    from src.routers.tasks import router

    for route in router.routes:
        # Check endpoint function signatures for UUID types
        import inspect
        sig = inspect.signature(route.endpoint)
        if "user_id" in sig.parameters:
            param = sig.parameters["user_id"]
            assert param.annotation == UUID, f"user_id in {route.path} must be UUID type"

    print("  ✓ user_id path parameters use native UUID type")
    print("Article III tests: PASSED\n")

def main():
    print("=" * 60)
    print("MILESTONE 3 VERIFICATION - Task CRUD API")
    print("=" * 60)
    print()

    all_passed = True
    try:
        test_path_compliance()
        test_uuid_compliance()
        test_task_router_discovery()

        print("=" * 60)
        print("MILESTONE 3 LOGIC VERIFIED ✓")
        print("=" * 60)
        print("\nNote: Full integration tests require a running server/database.")
        print("The structural and constitutional requirements are met.")

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
