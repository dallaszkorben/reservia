import sys
import os
import shutil
import logging
import time
import hashlib
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database
from backend.app.application import ReserviaApp

# Color constants
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Test configuration constants
HOME = str(Path.home())
TEST_DIR_NAME = '.reservia_test'
TEST_APP_NAME = 'reservia_test'
TEST_DB_NAME = 'test_reservia.db'

def hash_password(password):
    """Hash password using SHA-256 (same as client-side)"""
    return hashlib.sha256(password.encode()).hexdigest()

def cleanup_test_databases():
    """Clean up test database files and reset singleton"""
    # Close database connection if exists
    if Database._instance is not None:
        Database._instance.session.close()
        Database._instance.engine.dispose()

    # Close all logging handlers to release file locks
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)

    # Reset singleton
    Database._instance = None

    test_path = os.path.join(HOME, TEST_DIR_NAME)

    if os.path.exists(test_path):
        shutil.rmtree(test_path)

# === User ===

def test_db_user_add():

    print("=== User add database tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'session': {'secret_key': 'test-secret-key'}
    }

    # Create Flask app for session support
    app = ReserviaApp(config_dict)

    with app.test_request_context():
        print("\nTesting database singleton pattern...")
        print("  Verifying singleton instance...")
        db1 = Database.get_instance(config_dict)
        db2 = Database.get_instance()
        assert db1 is db2, "Database should be singleton"

        print("\nTesting user creation without login...")
        print("  Attempting to create user without admin login...")
        success, user, error_code, _ = db1.create_user("John Doe", "john@example.com", "password123")
        assert not success and user is None and error_code == "UNAUTHORIZED"

        print("\nTesting admin login and user creation...")
        print("  Logging in as admin...")
        _, admin_user, _, _ = db1.login("admin", hash_password("admin"))
        assert admin_user is not None

        print("  Creating user as admin...")
        _, user, _, _ = db1.create_user("John Doe", "john@example.com", hash_password("password123"))
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.id is not None

        print("\nTesting user retrieval...")
        print("  Getting all users from database...")
        users = db1.get_users()
        assert len(users) >= 2
        assert any(u.email == "john@example.com" for u in users)
        assert any(u.email == "admin@admin.se" for u in users)

    print(f"{GREEN}User add database tests passed!{RESET}")

def test_db_user_update():

    print("=== User update database tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'session': {'secret_key': 'test-secret-key'}
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        print("\nTesting user update without login...")
        print("  Attempting to update user without login...")
        result = db.update_user(email="test@example.com")
        assert result is None, "Should not update user without login"

        print("\nTesting user update with admin login...")
        print("  Logging in as admin...")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None

        print("  Updating email only...")
        updated_user = db.update_user(email="admin.new@admin.se")
        assert updated_user.email == "admin.new@admin.se"
        assert updated_user.name == "admin"

        print("  Updating password only...")
        updated_user = db.update_user(password=hash_password("newpass456"))
        assert updated_user is not None

        print("  Updating both email and password...")
        updated_user = db.update_user(email="admin.final@admin.se", password=hash_password("finalpass789"))
        assert updated_user.email == "admin.final@admin.se"

        print("  Verifying session was updated...")
        current_user = db.get_current_user()
        assert current_user['user_email'] == "admin.final@admin.se"

    print(f"{GREEN}User update database tests passed!{RESET}")

# === Resource ===

def test_db_resource_add():

    print("=== Resource add database tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'session': {'secret_key': 'test-secret-key'}
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        print("\nTesting resource creation without login...")
        print("  Attempting to create resource without admin login...")
        success, resource, error_code, _ = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert not success and resource is None and error_code == "UNAUTHORIZED"

        print("\nTesting resource creation with admin login...")
        print("  Logging in as admin...")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None

        print("  Creating resource with comment...")
        _, resource1, _, _ = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert resource1.name == "Meeting Room"
        assert resource1.comment == "Conference room for 10 people"
        assert resource1.id is not None

        print("  Creating resource without comment...")
        _, resource2, _, _ = db.create_resource("Projector")
        assert resource2.name == "Projector"
        assert resource2.comment is None
        assert resource2.id is not None

        print("\nTesting resource retrieval...")
        print("  Getting all resources from database...")
        _, resources, _, _ = db.get_resources()
        assert len(resources) == 2
        assert any(r.name == "Meeting Room" for r in resources)
        assert any(r.name == "Projector" for r in resources)

    print(f"{GREEN}Resource add database tests passed!{RESET}")


def test_db_resource_get_all():
    print("=== Resource get all database tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'session': {'secret_key': 'test-secret-key'}
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        operation += 1
        print(f"\n{operation}. Unauthorized access test")
        success, resources, error_code, error_msg = db.get_resources()
        assert not success and resources is None and error_code == "UNAUTHORIZED"

        operation += 1
        print(f"\n{operation}. Admin login test")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None

        operation += 1
        print(f"\n{operation}. Create test resources")
        _, resource1, _, _ = db.create_resource("Meeting Room A", "Conference room")
        _, resource2, _, _ = db.create_resource("Projector", "HD projector")
        _, resource3, _, _ = db.create_resource("Whiteboard")
        assert resource1 is not None and resource2 is not None and resource3 is not None

        operation += 1
        print(f"\n{operation}. Get all resources test")
        success, resources, error_code, error_msg = db.get_resources()
        assert success and resources is not None and error_code is None
        assert len(resources) == 3
        assert any(r.name == "Meeting Room A" for r in resources)
        assert any(r.name == "Projector" for r in resources)
        assert any(r.name == "Whiteboard" for r in resources)

    print(f"{GREEN}Resource get all database tests passed!{RESET}")

def test_db_resource_modify():
    print("=== Resource modify database tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'session': {'secret_key': 'test-secret-key'}
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        operation += 1
        print(f"\n{operation}. Unauthorized modification test")
        success, resource, error_code, error_msg = db.modify_resource(1, "Hacked Room")
        assert not success and resource is None and error_code == "UNAUTHORIZED"

        operation += 1
        print(f"\n{operation}. Admin login and create test resource")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None
        _, test_resource, _, _ = db.create_resource("Original Room", "Original comment")
        resource_id = test_resource.id

        operation += 1
        print(f"\n{operation}. Modify resource name only")
        success, modified_resource, error_code, error_msg = db.modify_resource(resource_id, name="Modified Room")
        assert success and modified_resource is not None and error_code is None
        assert modified_resource.name == "Modified Room"
        assert modified_resource.comment == "Original comment"

        operation += 1
        print(f"\n{operation}. Modify resource comment only")
        success, modified_resource, error_code, error_msg = db.modify_resource(resource_id, comment="Modified comment")
        assert success and modified_resource is not None and error_code is None
        assert modified_resource.name == "Modified Room"
        assert modified_resource.comment == "Modified comment"

        operation += 1
        print(f"\n{operation}. Modify both name and comment")
        success, modified_resource, error_code, error_msg = db.modify_resource(resource_id, name="Final Room", comment="Final comment")
        assert success and modified_resource is not None and error_code is None
        assert modified_resource.name == "Final Room"
        assert modified_resource.comment == "Final comment"

        operation += 1
        print(f"\n{operation}. Non-existent resource test")
        success, resource, error_code, error_msg = db.modify_resource(999, name="Non-existent")
        assert not success and resource is None and error_code == "RESOURCE_NOT_FOUND"
        assert "999" in error_msg and "not found" in error_msg

        operation += 1
        print(f"\n{operation}. Duplicate name test")
        _, another_resource, _, _ = db.create_resource("Another Room", "Another comment")
        success, resource, error_code, error_msg = db.modify_resource(resource_id, name="Another Room")
        assert not success and resource is None and error_code == "RESOURCE_EXISTS"
        assert "Another Room" in error_msg and "already exists" in error_msg

        operation += 1
        print(f"\n{operation}. Create regular user and test unauthorized access")
        _, regular_user, _, _ = db.create_user("testuser", "test@example.com", hash_password("pass123"))
        db.logout()
        _, _, _, _ = db.login("testuser", hash_password("pass123"))
        success, resource, error_code, error_msg = db.modify_resource(resource_id, name="Hacked Room")
        assert not success and resource is None and error_code == "UNAUTHORIZED"
        assert "Admin access required" in error_msg

    print(f"{GREEN}Resource modify database tests passed!{RESET}")

# === Login ===

def test_db_login():
    print("=== Database login tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        print("\nTesting login with default admin user...")
        print("  Attempting admin login...")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None
        assert admin_user.name == "admin"
        assert admin_user.email == "admin@admin.se"

        print("\nTesting login with wrong password...")
        print("  Attempting login with incorrect password...")
        success, result, error_code, _ = db.login("admin", hash_password("wrongpassword"))
        assert not success and result is None and error_code == "INVALID_PASSWORD"

        print("\nTesting login with non-existent user...")
        print("  Attempting login with non-existent user...")
        success, result, error_code, _ = db.login("nonexistent", hash_password("password"))
        assert not success and result is None and error_code == "USER_NOT_FOUND"

        print("\nTesting login with new user...")
        print("  Creating new test user...")
        _, _, _, _ = db.create_user("testuser", "test@example.com", hash_password("testpass123"))
        print("  Attempting login with new user...")
        _, test_user, _, _ = db.login("testuser", hash_password("testpass123"))
        assert test_user is not None
        assert test_user.name == "testuser"
        assert test_user.email == "test@example.com"

    print(f"{GREEN}Database login tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_user_add()
        test_db_resource_add()
        test_db_resource_get_all()
        test_db_resource_modify()
        test_db_user_update()
        test_db_login()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise