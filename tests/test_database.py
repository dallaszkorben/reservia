import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database

def test_database():
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
    test_database()