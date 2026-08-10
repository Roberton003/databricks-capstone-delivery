"""
Test script for Support Ticket System - Local Validation
This validates the app logic without needing Databricks environment.
"""

import sys
import os

# Mock the databricks SDK since we're running locally
class MockSecret:
    value = "cG9zdGdyZXM6Ly9yb2xlOnBhc3NAaG9zdDo1NDMyL2RhdGFiYXNlP3NzbG1vZGU9cmVxdWlyZQ=="

class MockSecrets:
    def get_secret(self, scope: str, key: str) -> MockSecret:
        return MockSecret()

class MockWorkspaceClient:
    secrets = MockSecrets()

sys.modules['databricks.sdk'] = type(sys)('databricks.sdk')
sys.modules['databricks.sdk'].WorkspaceClient = MockWorkspaceClient

# Now import the app
import app

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    assert hasattr(app, 'app'), "Flask app not found"
    assert hasattr(app, 'get_tickets'), "get_tickets function not found"
    assert hasattr(app, 'create_ticket'), "create_ticket function not found"
    assert hasattr(app, 'add_message'), "add_message function not found"
    assert hasattr(app, 'update_ticket_status'), "update_ticket_status function not found"
    assert hasattr(app, 'get_ticket_statistics'), "get_ticket_statistics function not found"
    print("✓ All imports and functions present")

def test_routes():
    """Test that all routes are defined."""
    print("\nTesting routes...")
    rules = [str(rule) for rule in app.app.url_map.iter_rules()]
    print(f"Found routes: {rules}")

    required_routes = ['/', '/tickets', '/tickets/<ticket_id>',
                      '/tickets/<ticket_id>/messages', '/tickets/<ticket_id>/status']
    for route in required_routes:
        assert route in rules, f"Route {route} not found"
    print("✓ All required routes present")

def test_validation():
    """Test input validation."""
    print("\nTesting validation...")

    # Valid input
    valid, error = app.validate_ticket_input("Test Ticket", "user@test.com")
    assert valid == True, "Valid input should pass"

    # Empty title
    valid, error = app.validate_ticket_input("", "user@test.com")
    assert valid == False, "Empty title should fail"
    assert "Title is required" in error

    # Empty created_by
    valid, error = app.validate_ticket_input("Test", "")
    assert valid == False, "Empty created_by should fail"
    print("✓ Validation working correctly")

def test_app_config():
    """Test Flask app configuration."""
    print("\nTesting Flask app configuration...")
    assert app.app.secret_key is not None, "Secret key should be set"
    assert app.app.testing == False, "App should not be in testing mode by default"
    print("✓ App configuration correct")

def main():
    """Run all tests."""
    print("=" * 50)
    print("Support Ticket System - Local Validation")
    print("=" * 50)

    try:
        test_imports()
        test_routes()
        test_validation()
        test_app_config()

        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
