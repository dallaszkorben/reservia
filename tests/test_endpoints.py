import sys
import os
import json
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
TEST_DIR_NAME = '.reservia_test_admin'
TEST_APP_NAME = 'reservia_test_admin'
TEST_DB_NAME = 'test_admin.db'

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

    # Small delay to ensure all resources are released
    time.sleep(0.1)

    test_path = os.path.join(HOME, TEST_DIR_NAME)

    if os.path.exists(test_path):
        shutil.rmtree(test_path)

def test_admin_user_add():
    print("=== Admin user add endpoint tests started!")
    
    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    # Create test app
    app = ReserviaApp(config_dict)

    with app.test_client() as client:
        print("\nTesting admin login...")
        print("  Logging in as admin...")
        login_response = client.post('/session/login',
                                   data=json.dumps({'name': 'admin', 'password': 'admin'}),
                                   content_type='application/json')
        assert login_response.status_code == 200

        print("\nTesting successful user creation...")
        print("  Creating user with all required fields...")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass123'}),
                             content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert 'user_id' in data

        print("\nTesting user creation with missing fields...")
        print("  Attempting to create user without required fields...")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'Test User'}),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    print(f"{GREEN}Admin user add tests passed!{RESET}")

def test_admin_resource_add():
    print("=== Admin resource add endpoint tests started!")
    
    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)

    with app.test_client() as client:
        print("\nTesting admin login...")
        print("  Logging in as admin...")
        login_response = client.post('/session/login',
                                   data=json.dumps({'name': 'admin', 'password': 'admin'}),
                                   content_type='application/json')
        assert login_response.status_code == 200

        print("\nTesting resource creation with comment...")
        print("  Creating resource with name and comment...")
        response = client.post('/admin/resource/add',
                             data=json.dumps({'name': 'Meeting Room', 'comment': 'Conference room'}),
                             content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Resource created successfully'
        assert 'resource_id' in data

        print("\nTesting resource creation without comment...")
        print("  Creating resource with name only...")
        response = client.post('/admin/resource/add',
                             data=json.dumps({'name': 'Projector'}),
                             content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Resource created successfully'

        print("\nTesting resource creation with missing name...")
        print("  Attempting to create resource without name field...")
        response = client.post('/admin/resource/add',
                             data=json.dumps({'comment': 'No name provided'}),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    print(f"{GREEN}Admin resource add tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_admin_user_add()
        test_admin_resource_add()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise