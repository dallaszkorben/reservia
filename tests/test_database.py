import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database
from backend.app.application import ReserviaApp

# Test configuration constants
TEST_DIR_NAME = '.reservia_test'
TEST_APP_NAME = 'reservia_test'
TEST_DB_NAME = 'test_reservia.db'

def cleanup_test_databases():
    """Clean up test database files and reset singleton"""
    HOME = str(Path.home())
    test_path = os.path.join(HOME, TEST_DIR_NAME)

    if os.path.exists(test_path):
        import shutil
        shutil.rmtree(test_path)

    # Reset singleton
    Database._instance = None

# === User ===

def test_db_user_add():
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
        # Test singleton pattern
        db1 = Database.get_instance(config_dict)
        db2 = Database.get_instance()
        assert db1 is db2, "Database should be singleton"

        # Test create user without login (should fail)
        user = db1.create_user("John Doe", "john@example.com", "password123")
        assert user is None, "Should not create user without admin login"

        # Login as admin first
        admin_user = db1.login("admin", "admin")
        assert admin_user is not None

        # Test create user as admin (should succeed)
        user = db1.create_user("John Doe", "john@example.com", "password123")
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.id is not None

        # Test get users (includes default admin + new user)
        users = db1.get_users()
        assert len(users) >= 2
        assert any(u.email == "john@example.com" for u in users)
        assert any(u.email == "admin@admin.se" for u in users)

    print("User add database tests passed!")

def test_db_user_update():
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

        # Test update without login (should fail)
        result = db.update_user(email="test@example.com")
        assert result is None, "Should not update user without login"

        # Login as admin
        admin_user = db.login("admin", "admin")
        assert admin_user is not None

        # Test update email only
        updated_user = db.update_user(email="admin.new@admin.se")
        assert updated_user.email == "admin.new@admin.se"
        assert updated_user.name == "admin"

        # Test update password only
        updated_user = db.update_user(password="newpass456")
        assert updated_user is not None

        # Test update both email and password
        updated_user = db.update_user(email="admin.final@admin.se", password="finalpass789")
        assert updated_user.email == "admin.final@admin.se"

        # Verify session was updated with new email
        current_user = db.get_current_user()
        assert current_user['user_email'] == "admin.final@admin.se"

    print("User update database tests passed!")

# === Resource ===

def test_db_resource_add():
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

        # Test create resource without login (should fail)
        resource = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert resource is None, "Should not create resource without admin login"

        # Login as admin first
        admin_user = db.login("admin", "admin")
        assert admin_user is not None

        # Test create resource with comment
        resource1 = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert resource1.name == "Meeting Room"
        assert resource1.comment == "Conference room for 10 people"
        assert resource1.id is not None

        # Test create resource without comment
        resource2 = db.create_resource("Projector")
        assert resource2.name == "Projector"
        assert resource2.comment is None
        assert resource2.id is not None

        # Test get resources
        resources = db.get_resources()
        assert len(resources) == 2
        assert any(r.name == "Meeting Room" for r in resources)
        assert any(r.name == "Projector" for r in resources)

    print("Resource add database tests passed!")



if __name__ == "__main__":
    test_db_user_add()
    test_db_resource_add()
    test_db_user_update()