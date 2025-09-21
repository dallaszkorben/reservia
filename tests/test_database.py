import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database

def cleanup_test_databases():
    """Clean up test database files and reset singleton"""
    HOME = str(Path.home())
    test_path = os.path.join(HOME, '.reservia_test')
    
    if os.path.exists(test_path):
        import shutil
        shutil.rmtree(test_path)

    # Reset singleton
    Database._instance = None

def test_db_user_add():
    cleanup_test_databases()

    config_dict = {
        'app_name': 'reservia_test',
        'database': {
            'name': 'test_reservia.db'
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

    print("All database tests passed!")

if __name__ == "__main__":
    test_db_user_add()