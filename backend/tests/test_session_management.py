"""
Session Management Test Suite

Comprehensive test suite for session management functionality, covering:
- Database session operations (login, logout, status)
- API endpoints for session management (/session/login, /session/logout, /session/status)
- Authentication and authorization
- Session state validation and persistence

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
TEST_DIR_NAME = '.reservia_test_session'
TEST_APP_NAME = 'reservia_test_session'
TEST_DB_NAME = 'test_session.db'

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

def test_db_session_login_logout():
    """
    Test complete database session management lifecycle including login, logout,
    session state validation, and authentication error handling.
    """
    print("=== Database session login/logout tests started!")
    
    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_request_context():
        db = Database.get_instance()

        operation += 1
        print(f"\n{operation}. Initial session state test")
        assert not db.is_logged_in()
        assert db.get_current_user() is None

        operation += 1
        print(f"\n{operation}. Successful admin login test")
        success, user, error_code, error_msg = db.login("admin", hash_password("admin"))
        assert success and user is not None
        assert user.name == "admin"
        assert user.email == "admin@admin.se"

        operation += 1
        print(f"\n{operation}. Session state after login test")
        assert db.is_logged_in()
        current_user = db.get_current_user()
        assert current_user is not None
        assert current_user['user_name'] == "admin"
        assert current_user['user_email'] == "admin@admin.se"

        operation += 1
        print(f"\n{operation}. Logout functionality test")
        success, data, error_code, error_msg = db.logout()
        assert success is True
        assert not db.is_logged_in()
        assert db.get_current_user() is None

    with app.test_request_context():
        operation += 1
        print(f"\n{operation}. Logout when not logged in test")
        success, data, error_code, error_msg = db.logout()
        assert success is False

        operation += 1
        print(f"\n{operation}. Failed login test")
        success, user, error_code, error_msg = db.login("admin", hash_password("wrongpassword"))
        assert not success and user is None
        assert not db.is_logged_in()

    print(f"{GREEN}Database session login/logout tests passed!{RESET}")

def test_db_authentication():
    """
    Test database authentication functionality including password validation,
    user existence checks, and error handling for invalid credentials.
    """
    print("=== Database authentication tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        operation += 1
        print(f"\n{operation}. Default admin login test")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None
        assert admin_user.name == "admin"
        assert admin_user.email == "admin@admin.se"

        operation += 1
        print(f"\n{operation}. Invalid password test")
        success, result, error_code, _ = db.login("admin", hash_password("wrongpassword"))
        assert not success and result is None and error_code == "INVALID_PASSWORD"

        operation += 1
        print(f"\n{operation}. Non-existent user test")
        success, result, error_code, _ = db.login("nonexistent", hash_password("password"))
        assert not success and result is None and error_code == "USER_NOT_FOUND"

        operation += 1
        print(f"\n{operation}. New user creation and login test")
        _, _, _, _ = db.create_user("testuser", "test@example.com", hash_password("testpass123"))
        _, test_user, _, _ = db.login("testuser", hash_password("testpass123"))
        assert test_user is not None
        assert test_user.name == "testuser"
        assert test_user.email == "test@example.com"

    print(f"{GREEN}Database authentication tests passed!{RESET}")

# === API Endpoint Tests ===

def test_api_session_login():
    """
    Test /session/login endpoint functionality including successful login,
    invalid credentials, and proper session establishment.
    """
    print("=== API session login endpoint tests started!")

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
        print(f"\n{operation}. Successful admin login test")
        response = client.post('/session/login',
                             data=json.dumps({'name': 'admin', 'password': hash_password('admin')}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert data['user_name'] == 'admin'

        operation += 1
        print(f"\n{operation}. Invalid password test")
        response = client.post('/session/login',
                             data=json.dumps({'name': 'admin', 'password': hash_password('wrongpassword')}),
                             content_type='application/json')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

        operation += 1
        print(f"\n{operation}. Non-existent user test")
        response = client.post('/session/login',
                             data=json.dumps({'name': 'nonexistent', 'password': hash_password('password')}),
                             content_type='application/json')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

        operation += 1
        print(f"\n{operation}. Missing fields validation test")
        response = client.post('/session/login',
                             data=json.dumps({'name': 'admin'}),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    print(f"{GREEN}API session login tests passed!{RESET}")

def test_api_session_logout():
    """
    Test /session/logout endpoint functionality including successful logout
    and proper session cleanup.
    """
    print("=== API session logout endpoint tests started!")

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
        print(f"\n{operation}. Login and logout test")
        client.post('/session/login',
                   data=json.dumps({'name': 'admin', 'password': hash_password('admin')}),
                   content_type='application/json')
        
        response = client.post('/session/logout')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logout successful'

        operation += 1
        print(f"\n{operation}. Logout when not logged in test")
        response = client.post('/session/logout')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'No active session' in data['message']

    print(f"{GREEN}API session logout tests passed!{RESET}")

def test_api_session_status():
    """
    Test /session/status endpoint functionality including logged-in/logged-out states,
    admin vs regular user status, and proper session data return.
    """
    print("=== API session status endpoint tests started!")

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
        print(f"\n{operation}. Session status when not logged in")
        response = client.get('/session/status')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['logged_in'] == False

        operation += 1
        print(f"\n{operation}. Admin login and status check")
        login_response = client.post('/session/login',
                                   data=json.dumps({'name': 'admin', 'password': hash_password('admin')}),
                                   content_type='application/json')
        assert login_response.status_code == 200

        status_response = client.get('/session/status')
        assert status_response.status_code == 200
        data = json.loads(status_response.data)
        assert data['logged_in'] == True
        assert data['user_name'] == 'admin'
        assert data['user_email'] == 'admin@admin.se'
        assert data['is_admin'] == True
        assert 'user_id' in data

        operation += 1
        print(f"\n{operation}. Create regular user and test status")
        client.post('/admin/user/add',
                   data=json.dumps({'name': 'testuser', 'email': 'test@example.com', 'password': hash_password('pass123')}),
                   content_type='application/json')
        client.post('/session/logout')

        client.post('/session/login',
                   data=json.dumps({'name': 'testuser', 'password': hash_password('pass123')}),
                   content_type='application/json')

        status_response = client.get('/session/status')
        assert status_response.status_code == 200
        data = json.loads(status_response.data)
        assert data['logged_in'] == True
        assert data['user_name'] == 'testuser'
        assert data['user_email'] == 'test@example.com'
        assert data['is_admin'] == False

    print(f"{GREEN}API session status tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_session_login_logout()
        test_db_authentication()
        test_api_session_login()
        test_api_session_logout()
        test_api_session_status()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise