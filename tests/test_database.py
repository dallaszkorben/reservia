import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database

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

def test_db_user_add():
    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'database': {
            'name': TEST_DB_NAME
        }
    }

    # Test singleton pattern
    db1 = Database.get_instance(config_dict)
    db2 = Database.get_instance()
    assert db1 is db2, "Database should be singleton"

    # Test create user
    user = db1.create_user("John Doe", "john@example.com")
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.id is not None

    # Test get users
    users = db1.get_users()
    assert len(users) >= 1
    assert any(u.email == "john@example.com" for u in users)

    print("User add database tests passed!")

def test_db_resource_add():
    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'database': {
            'name': TEST_DB_NAME
        }
    }

    db = Database.get_instance(config_dict)

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
    assert len(resources) >= 2
    assert any(r.name == "Meeting Room" for r in resources)
    assert any(r.name == "Projector" for r in resources)

    print("Resource add database tests passed!")

if __name__ == "__main__":
    test_db_user_add()
    test_db_resource_add()