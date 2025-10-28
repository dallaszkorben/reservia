"""
Resource Management Test Suite

Comprehensive test suite for resource management functionality, covering:
- Database resource operations (create, modify, retrieve)
- API endpoints for resource management (/admin/resource/add, /admin/resource/modify, /info/resources)
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
TEST_DIR_NAME = '.reservia_test_resources'
TEST_APP_NAME = 'reservia_test_resources'
TEST_DB_NAME = 'test_resources.db'

def hash_password(password):
    """Hash password using SHA-256 (same as client-side)"""
    return hashlib.sha256(password.encode()).hexdigest()

def cleanup_test_databases():
    """Clean up test database files and reset singleton"""
    if Database._instance is not None:
        try:
            Database._instance.session.close()
            Database._instance.engine.dispose()
        except:
            pass

    for handler in logging.root.handlers[:]:
        try:
            handler.close()
            logging.root.removeHandler(handler)
        except:
            pass

    Database._instance = None
    time.sleep(0.2)

    test_path = os.path.join(HOME, TEST_DIR_NAME)
    if os.path.exists(test_path):
        try:
            shutil.rmtree(test_path)
        except OSError:
            # Force removal if normal removal fails
            import subprocess
            subprocess.run(['rm', '-rf', test_path], check=False)
        except OSError:
            # Force removal if normal removal fails
            import subprocess
            subprocess.run(['rm', '-rf', test_path], check=False)

# === Database Layer Tests ===

def test_db_resource_create():
    """
    Test database resource creation functionality including authorization checks
    and resource retrieval with optional comments.
    """
    print("=== Database resource create tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'session': {'secret_key': 'test-secret-key'}
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        operation += 1
        print(f"\n{operation}. Unauthorized resource creation test")
        success, resource, error_code, _ = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert not success and resource is None and error_code == "UNAUTHORIZED"

        operation += 1
        print(f"\n{operation}. Admin login test")
        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert admin_user is not None

        operation += 1
        print(f"\n{operation}. Resource creation with comment test")
        _, resource1, _, _ = db.create_resource("Meeting Room", "Conference room for 10 people")
        assert resource1.name == "Meeting Room"
        assert resource1.comment == "Conference room for 10 people"
        assert resource1.id is not None

        operation += 1
        print(f"\n{operation}. Resource creation without comment test")
        _, resource2, _, _ = db.create_resource("Projector")
        assert resource2.name == "Projector"
        assert resource2.comment is None
        assert resource2.id is not None

        operation += 1
        print(f"\n{operation}. Resource retrieval test")
        _, resources, _, _ = db.get_resources()
        assert len(resources) == 2
        assert any(r.name == "Meeting Room" for r in resources)
        assert any(r.name == "Projector" for r in resources)

    print(f"{GREEN}Database resource create tests passed!{RESET}")

def test_db_resource_get_all():
    """
    Test database resource retrieval functionality with authorization checks
    and multiple resource creation scenarios.
    """
    print("=== Database resource get all tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
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

    print(f"{GREEN}Database resource get all tests passed!{RESET}")

def test_db_resource_modify():
    """
    Test database resource modification functionality including name/comment updates,
    authorization checks, and error handling for duplicates and non-existent resources.
    """
    print("=== Database resource modify tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
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

    print(f"{GREEN}Database resource modify tests passed!{RESET}")

# === API Endpoint Tests ===

def test_api_resource_add():
    """
    Test /admin/resource/add endpoint functionality including resource creation
    with/without comments, duplicate validation, and field validation.
    """
    print("=== API resource add endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
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
        print(f"\n{operation}. Resource creation with comment test")
        response = client.post('/admin/resource/add',
                             data=json.dumps({'name': 'Meeting Room', 'comment': 'Conference room'}),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Resource created successfully'
        assert 'resource_id' in data

        operation += 1
        print(f"\n{operation}. Resource creation without comment test")
        response = client.post('/admin/resource/add',
                             data=json.dumps({'name': 'Projector'}),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Resource created successfully'

        operation += 1
        print(f"\n{operation}. Duplicate resource name test")
        response = client.post('/admin/resource/add',
                             data=json.dumps({'name': 'Meeting Room', 'comment': 'Duplicate room'}),
                             content_type='application/json')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Meeting Room' in data['error']
        assert 'already exists' in data['error']

        operation += 1
        print(f"\n{operation}. Missing name field validation test")
        response = client.post('/admin/resource/add',
                             data=json.dumps({'comment': 'No name provided'}),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    print(f"{GREEN}API resource add tests passed!{RESET}")

def test_api_resource_modify():
    """
    Test /admin/resource/modify endpoint functionality including name/comment updates,
    duplicate validation, authorization checks, and field validation.
    """
    print("=== API resource modify endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        operation += 1
        print(f"\n{operation}. Admin login and create test resource")
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        resp = client.post('/admin/resource/add', data=json.dumps({'name': 'Test Room', 'comment': 'Original comment'}), content_type='application/json')
        resource_id = json.loads(resp.data)['resource_id']

        operation += 1
        print(f"\n{operation}. Admin modifies resource name")
        response = client.post('/admin/resource/modify', data=json.dumps({'resource_id': resource_id, 'name': 'Modified Room'}), content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Resource modified successfully'

        operation += 1
        print(f"\n{operation}. Admin modifies resource comment")
        response = client.post('/admin/resource/modify', data=json.dumps({'resource_id': resource_id, 'comment': 'Updated comment'}), content_type='application/json')
        assert response.status_code == 200

        operation += 1
        print(f"\n{operation}. Duplicate resource name test")
        client.post('/admin/resource/add', data=json.dumps({'name': 'Another Room', 'comment': 'Another comment'}), content_type='application/json')
        response = client.post('/admin/resource/modify', data=json.dumps({'resource_id': resource_id, 'name': 'Another Room'}), content_type='application/json')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Another Room' in data['error']
        assert 'already exists' in data['error']

        operation += 1
        print(f"\n{operation}. Non-existent resource test")
        response = client.post('/admin/resource/modify', data=json.dumps({'resource_id': 999, 'name': 'Non-existent'}), content_type='application/json')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert '999' in data['error']
        assert 'not found' in data['error']

    print(f"{GREEN}API resource modify tests passed!{RESET}")

def test_api_info_resources():
    """
    Test /info/resources endpoint functionality including resource retrieval
    and proper data formatting.
    """
    print("=== API info resources endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        operation += 1
        print(f"\n{operation}. Admin login and create test resources")
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        client.post('/admin/resource/add', data=json.dumps({'name': 'Meeting Room', 'comment': 'Conference room'}), content_type='application/json')
        client.post('/admin/resource/add', data=json.dumps({'name': 'Projector'}), content_type='application/json')

        operation += 1
        print(f"\n{operation}. Get all resources test")
        response = client.get('/info/resources')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Resources retrieved successfully'
        assert 'resources' in data
        assert data['count'] == 2

        resource_names = [r['name'] for r in data['resources']]
        assert 'Meeting Room' in resource_names
        assert 'Projector' in resource_names

    print(f"{GREEN}API info resources tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_resource_create()
        test_db_resource_get_all()
        test_db_resource_modify()
        test_api_resource_add()
        test_api_resource_modify()
        test_api_info_resources()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise