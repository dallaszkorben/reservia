"""
User Management Test Suite

Comprehensive test suite for user management functionality, covering:
- Database user operations (create, modify, retrieve)
- API endpoints for user management (/admin/user/add, /admin/user/modify, /info/users)
- Authorization and access control
- Field validation and error handling

All tests use isolated test databases and proper cleanup.
"""

import sys
import os
import json
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
TEST_DIR_NAME = '.reservia_test_users'
TEST_APP_NAME = 'reservia_test_users'
TEST_DB_NAME = 'test_users.db'

def hash_password(password):
    """Hash password using SHA-256 (same as client-side)"""
    return hashlib.sha256(password.encode()).hexdigest()

def cleanup_test_databases():
    """Clean up test database files and reset singleton"""
    if Database._instance is not None:
        Database._instance.session.close()
        Database._instance.engine.dispose()

    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)

    Database._instance = None
    time.sleep(0.1)

    test_path = os.path.join(HOME, TEST_DIR_NAME)
    if os.path.exists(test_path):
        shutil.rmtree(test_path)

# === Database Layer Tests ===

def test_db_user_create():
    """
    Test database user creation functionality including authorization checks,
    singleton pattern verification, and user retrieval.
    """
    print("=== Database user create tests started!")

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
        operation += 1
        print(f"\n{operation}. Database singleton pattern test")
        db1 = Database.get_instance(config_dict)
        db2 = Database.get_instance()
        assert db1 is db2, "Database should be singleton"

        operation += 1
        print(f"\n{operation}. Unauthorized user creation test")
        success, user, error_code, _ = db1.create_user("John Doe", "john@example.com", "password123")
        assert not success and user is None and error_code == "UNAUTHORIZED"

        operation += 1
        print(f"\n{operation}. Admin login test")
        _, admin_user, _, _ = db1.login("admin", hash_password("admin"))
        assert admin_user is not None

        operation += 1
        print(f"\n{operation}. User creation as admin test")
        _, user, _, _ = db1.create_user("John Doe", "john@example.com", hash_password("password123"))
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.id is not None

        operation += 1
        print(f"\n{operation}. User retrieval test")
        success, users, _, _ = db1.get_users()
        assert success and len(users) >= 2
        assert any(u['email'] == "john@example.com" for u in users)
        assert any(u['email'] == "admin@admin.se" for u in users)

    print(f"{GREEN}Database user create tests passed!{RESET}")

def test_db_user_modify():
    """
    Test database user modification functionality including admin/self modification,
    authorization checks, and field validation.
    """
    print("=== Database user modify tests started!")

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
        print(f"\n{operation}. Setup test data")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None
        _, test_user, _, _ = db.create_user("testuser", "test@example.com", hash_password("pass123"))
        user_id = test_user.id

        operation += 1
        print(f"\n{operation}. Admin modifies user email")
        success, modified_user, error_code, error_msg = db.modify_user(user_id, email="newemail@example.com")
        assert success and modified_user is not None and error_code is None
        assert modified_user.email == "newemail@example.com"

        operation += 1
        print(f"\n{operation}. Admin modifies user password")
        success, modified_user, error_code, error_msg = db.modify_user(user_id, password=hash_password("newpass456"))
        assert success and modified_user is not None and error_code is None

        operation += 1
        print(f"\n{operation}. User modifies own data")
        db.logout()
        _, _, _, _ = db.login("testuser", hash_password("newpass456"))
        success, modified_user, error_code, error_msg = db.modify_user(user_id, email="selfmodified@example.com")
        assert success and modified_user is not None and error_code is None
        assert modified_user.email == "selfmodified@example.com"

        operation += 1
        print(f"\n{operation}. User cannot modify other user")
        db.logout()
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        _, user2, _, _ = db.create_user("user2", "user2@example.com", hash_password("pass2"))
        user2_id = user2.id
        db.logout()
        _, _, _, _ = db.login("testuser", hash_password("newpass456"))
        success, result, error_code, error_msg = db.modify_user(user2_id, email="hacked@example.com")
        assert not success and result is None and error_code == "UNAUTHORIZED"

    print(f"{GREEN}Database user modify tests passed!{RESET}")

def test_db_user_update():
    """
    Test database user profile update functionality for logged-in users,
    including email and password modifications.
    """
    print("=== Database user update tests started!")

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
        print(f"\n{operation}. Unauthorized user update test")
        result = db.update_user(email="test@example.com")
        assert result is None, "Should not update user without login"

        operation += 1
        print(f"\n{operation}. Admin login test")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None

        operation += 1
        print(f"\n{operation}. Update email only test")
        updated_user = db.update_user(email="admin.new@admin.se")
        assert updated_user.email == "admin.new@admin.se"
        assert updated_user.name == "admin"

        operation += 1
        print(f"\n{operation}. Update password only test")
        updated_user = db.update_user(password=hash_password("newpass456"))
        assert updated_user is not None

        operation += 1
        print(f"\n{operation}. Update both email and password test")
        updated_user = db.update_user(email="admin.final@admin.se", password=hash_password("finalpass789"))
        assert updated_user.email == "admin.final@admin.se"

        operation += 1
        print(f"\n{operation}. Session update verification test")
        current_user = db.get_current_user()
        assert current_user['user_email'] == "admin.final@admin.se"

    print(f"{GREEN}Database user update tests passed!{RESET}")

def test_db_get_users():
    """
    Test secure user retrieval functionality with admin-only access control
    and proper user data formatting as dictionaries.
    """
    print("=== Database get users tests started!")

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
        success, users, error_code, error_msg = db.get_users()
        assert not success and users is None and error_code == "UNAUTHORIZED"
        assert "Admin access required" in error_msg

        operation += 1
        print(f"\n{operation}. Admin login test")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None

        operation += 1
        print(f"\n{operation}. Get users as admin (only default admin exists)")
        success, users, error_code, error_msg = db.get_users()
        assert success and users is not None and error_code is None
        assert len(users) == 1
        assert users[0]['name'] == 'admin'
        assert users[0]['email'] == 'admin@admin.se'
        assert users[0]['is_admin'] == True
        assert 'id' in users[0]

        operation += 1
        print(f"\n{operation}. Create additional users and test")
        _, user1, _, _ = db.create_user("John Doe", "john@example.com", hash_password("pass123"))
        _, user2, _, _ = db.create_user("Jane Smith", "jane@example.com", hash_password("pass456"))
        success, users, error_code, error_msg = db.get_users()
        assert success and len(users) == 3

        user_names = [u['name'] for u in users]
        assert 'admin' in user_names
        assert 'John Doe' in user_names
        assert 'Jane Smith' in user_names

        for user in users:
            assert 'id' in user
            assert 'name' in user
            assert 'email' in user
            assert 'is_admin' in user

        operation += 1
        print(f"\n{operation}. Test regular user cannot access")
        db.logout()
        _, _, _, _ = db.login("John Doe", hash_password("pass123"))
        success, users, error_code, error_msg = db.get_users()
        assert not success and users is None and error_code == "UNAUTHORIZED"
        assert "Admin access required" in error_msg

    print(f"{GREEN}Database get users tests passed!{RESET}")

# === API Endpoint Tests ===

def test_api_user_add():
    """
    Test /admin/user/add endpoint functionality including successful user creation,
    duplicate validation, field validation, and authorization checks.
    """
    print("=== API user add endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        operation += 1
        print(f"\n{operation}. Admin login test")
        login_response = client.post('/session/login',
                                   data=json.dumps({'name': 'admin', 'password': hash_password('admin')}),
                                   content_type='application/json')
        assert login_response.status_code == 200

        operation += 1
        print(f"\n{operation}. Successful user creation test")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'testuser', 'email': 'test@example.com', 'password': hash_password('pass123')}),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert 'user_id' in data

        operation += 1
        print(f"\n{operation}. Duplicate username test")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'testuser', 'email': 'different@example.com', 'password': hash_password('pass456')}),
                             content_type='application/json')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
        assert 'testuser' in data['error']
        assert 'already exists' in data['error']

        operation += 1
        print(f"\n{operation}. Missing fields validation test")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'Test User'}),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    print(f"{GREEN}API user add tests passed!{RESET}")

def test_api_user_modify():
    """
    Test /admin/user/modify endpoint functionality including admin modifications,
    self-modification, authorization checks, and field validation.
    """
    print("=== API user modify endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        operation += 1
        print(f"\n{operation}. Admin login and create test user")
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        resp = client.post('/admin/user/add', data=json.dumps({'name': 'testuser', 'email': 'test@example.com', 'password': hash_password('pass123')}), content_type='application/json')
        user_id = json.loads(resp.data)['user_id']

        operation += 1
        print(f"\n{operation}. Admin modifies user email")
        response = client.post('/admin/user/modify', data=json.dumps({'user_id': user_id, 'email': 'newemail@example.com'}), content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User modified successfully'

        operation += 1
        print(f"\n{operation}. User modifies own data")
        client.post('/session/logout')
        client.post('/session/login', data=json.dumps({'name': 'testuser', 'password': hash_password('pass123')}), content_type='application/json')
        response = client.post('/admin/user/modify', data=json.dumps({'user_id': user_id, 'email': 'selfmodified@example.com'}), content_type='application/json')
        assert response.status_code == 200

        operation += 1
        print(f"\n{operation}. User cannot modify other user")
        client.post('/session/logout')
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        resp2 = client.post('/admin/user/add', data=json.dumps({'name': 'user2', 'email': 'user2@example.com', 'password': hash_password('pass2')}), content_type='application/json')
        user2_id = json.loads(resp2.data)['user_id']
        client.post('/session/logout')
        client.post('/session/login', data=json.dumps({'name': 'testuser', 'password': hash_password('pass123')}), content_type='application/json')
        response = client.post('/admin/user/modify', data=json.dumps({'user_id': user2_id, 'email': 'hacked@example.com'}), content_type='application/json')
        assert response.status_code == 403

    print(f"{GREEN}API user modify tests passed!{RESET}")

def test_api_info_users():
    """
    Test /info/users endpoint functionality including admin-only access control,
    proper user data formatting, and field validation.
    """
    print("=== API info users endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        operation += 1
        print(f"\n{operation}. Unauthorized access test")
        response = client.get('/info/users')
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Admin access required' in data['error']

        operation += 1
        print(f"\n{operation}. Admin login test")
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        response = client.get('/info/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Users retrieved successfully'
        assert 'users' in data
        assert data['count'] == 1

        operation += 1
        print(f"\n{operation}. Create additional users and test")
        client.post('/admin/user/add', data=json.dumps({'name': 'John Doe', 'email': 'john@example.com', 'password': hash_password('pass123')}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'Jane Smith', 'email': 'jane@example.com', 'password': hash_password('pass456')}), content_type='application/json')
        
        response = client.get('/info/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 3
        
        user_names = [u['name'] for u in data['users']]
        assert 'admin' in user_names
        assert 'John Doe' in user_names
        assert 'Jane Smith' in user_names

    print(f"{GREEN}API info users tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_user_create()
        test_db_user_modify()
        test_db_user_update()
        test_db_get_users()
        test_api_user_add()
        test_api_user_modify()
        test_api_info_users()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise