import sys
import os
import shutil
import logging
import time
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
        user = db1.create_user("John Doe", "john@example.com", "password123")
        assert user is None, "Should not create user without admin login"

        print("\nTesting admin login and user creation...")
        print("  Logging in as admin...")
        admin_user = db1.login("admin", "admin")
        assert admin_user is not None

        print("  Creating user as admin...")
        user = db1.create_user("John Doe", "john@example.com", "password123")
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
        admin_user = db.login("admin", "admin")
        assert admin_user is not None

        print("  Updating email only...")
        updated_user = db.update_user(email="admin.new@admin.se")
        assert updated_user.email == "admin.new@admin.se"
        assert updated_user.name == "admin"

        print("  Updating password only...")
        updated_user = db.update_user(password="newpass456")
        assert updated_user is not None

        print("  Updating both email and password...")
        updated_user = db.update_user(email="admin.final@admin.se", password="finalpass789")
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
        resource = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert resource is None, "Should not create resource without admin login"

        print("\nTesting resource creation with admin login...")
        print("  Logging in as admin...")
        admin_user = db.login("admin", "admin")
        assert admin_user is not None

        print("  Creating resource with comment...")
        resource1 = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert resource1.name == "Meeting Room"
        assert resource1.comment == "Conference room for 10 people"
        assert resource1.id is not None

        print("  Creating resource without comment...")
        resource2 = db.create_resource("Projector")
        assert resource2.name == "Projector"
        assert resource2.comment is None
        assert resource2.id is not None

        print("\nTesting resource retrieval...")
        print("  Getting all resources from database...")
        resources = db.get_resources()
        assert len(resources) == 2
        assert any(r.name == "Meeting Room" for r in resources)
        assert any(r.name == "Projector" for r in resources)

    print(f"{GREEN}Resource add database tests passed!{RESET}")

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
        admin_user = db.login("admin", "admin")
        assert admin_user is not None
        assert admin_user.name == "admin"
        assert admin_user.email == "admin@admin.se"

        print("\nTesting login with wrong password...")
        print("  Attempting login with incorrect password...")
        result = db.login("admin", "wrongpassword")
        assert result is None

        print("\nTesting login with non-existent user...")
        print("  Attempting login with non-existent user...")
        result = db.login("nonexistent", "password")
        assert result is None

        print("\nTesting login with new user...")
        print("  Creating new test user...")
        db.create_user("testuser", "test@example.com", "testpass123")
        print("  Attempting login with new user...")
        test_user = db.login("testuser", "testpass123")
        assert test_user is not None
        assert test_user.name == "testuser"
        assert test_user.email == "test@example.com"

    print(f"{GREEN}Database login tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_user_add()
        test_db_resource_add()
        test_db_user_update()
        test_db_login()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise