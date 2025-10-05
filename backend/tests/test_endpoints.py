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

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        operation += 1
        print(f"\n{operation}. Admin login test")
        login_response = client.post('/session/login',
                                   data=json.dumps({'name': 'admin', 'password': 'admin'}),
                                   content_type='application/json')
        assert login_response.status_code == 200

        operation += 1
        print(f"\n{operation}. Successful user creation test")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'testuser', 'email': 'test@example.com', 'password': 'pass123'}),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert 'user_id' in data

        operation += 1
        print(f"\n{operation}. Duplicate username test")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'testuser', 'email': 'different@example.com', 'password': 'pass456'}),
                             content_type='application/json')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
        assert 'testuser' in data['error']
        assert 'already exists' in data['error']

        operation += 1
        print(f"\n{operation}. Duplicate email test")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'differentuser', 'email': 'test@example.com', 'password': 'pass789'}),
                             content_type='application/json')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
        assert 'test@example.com' in data['error']
        assert 'already exists' in data['error']

        operation += 1
        print(f"\n{operation}. Missing fields validation test")
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'Test User'}),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    print(f"{GREEN}Admin user add tests passed!{RESET}\n")


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
    operation = 0

    with app.test_client() as client:
        operation += 1
        print(f"\n{operation}. Admin login test")
        login_response = client.post('/session/login',
                                   data=json.dumps({'name': 'admin', 'password': 'admin'}),
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

    print(f"{GREEN}Admin resource add tests passed!{RESET}\n")


def test_endpoint_reservation_lifecycle():
    print("=== Endpoint reservation lifecycle tests started!")

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
        # Setup: Create users and resources
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': 'admin'}), content_type='application/json')

        client.post('/admin/user/add', data=json.dumps({'name': 'user1', 'email': 'user1@example.com', 'password': 'pass1'}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user2', 'email': 'user2@example.com', 'password': 'pass2'}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user3', 'email': 'user3@example.com', 'password': 'pass3'}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user4', 'email': 'user4@example.com', 'password': 'pass4'}), content_type='application/json')

        resp1 = client.post('/admin/resource/add', data=json.dumps({'name': 'resource1', 'comment': 'Test resource 1'}), content_type='application/json')
        resp2 = client.post('/admin/resource/add', data=json.dumps({'name': 'resource2', 'comment': 'Test resource 2'}), content_type='application/json')

        resource1_id = json.loads(resp1.data)['resource_id']
        resource2_id = json.loads(resp2.data)['resource_id']

        client.post('/session/logout')

        # --------------------------------
        # 1. Multiple reservation requests
        # --------------------------------
        operation += 1
        print(f"\n{operation}. Multiple reservation requests")

        # User1-4 request resource1
        for user in ['user1', 'user2', 'user3', 'user4']:
            client.post('/session/login', data=json.dumps({'name': user, 'password': f'pass{user[-1]}'}), content_type='application/json')
            client.post('/reservation/request', data=json.dumps({'resource_id': resource1_id}), content_type='application/json')
            client.post('/session/logout')

        # User1-2 request resource2
        for user in ['user1', 'user2']:
            client.post('/session/login', data=json.dumps({'name': user, 'password': f'pass{user[-1]}'}), content_type='application/json')
            client.post('/reservation/request', data=json.dumps({'resource_id': resource2_id}), content_type='application/json')
            client.post('/session/logout')

        # Get reservations for resource1
        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': 'pass1'}), content_type='application/json')
        resp = client.get(f'/reservation/active?resource_id={resource1_id}')
        reservations1 = json.loads(resp.data)['reservations']

        print(f"Resource1 reservations:")
        for r in reservations1:
            user_name = r['user_name']
            if user_name == 'user1':
                assert r['status'] == 'approved'
            else:
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        # Get reservations for resource2
        resp = client.get(f'/reservation/active?resource_id={resource2_id}')
        reservations2 = json.loads(resp.data)['reservations']

        print(f"Resource2 reservations:")
        for r in reservations2:
            user_name = r['user_name']
            if user_name == 'user1':
                assert r['status'] == 'approved'
            else:
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        client.post('/session/logout')

        # -------------------------------------------------------------
        # 2. User1 cancels - not successfuly - reservation on resource1
        # -------------------------------------------------------------
        operation += 1
        print(f"\n{operation}. User1 cancels (not successfuly) reservation on resource1")

        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': 'pass1'}), content_type='application/json')
        client.post('/reservation/cancel', data=json.dumps({'resource_id': resource1_id}), content_type='application/json')

        # Get updated reservations for resource1
        resp = client.get(f'/reservation/active?resource_id={resource1_id}')
        reservations1 = json.loads(resp.data)['reservations']

        print(f"Resource1 reservations after user1 cancel:")
        for r in reservations1:
            user_name = r['user_name']
            if user_name == 'user1':
                assert r['status'] == 'approved'
            elif user_name in ['user2', 'user3', 'user4']:
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        # Get reservations for resource2 (should be unchanged)
        resp = client.get(f'/reservation/active?resource_id={resource2_id}')
        reservations2 = json.loads(resp.data)['reservations']

        print(f"Resource2 reservations (unchanged):")
        for r in reservations2:
            user_name = r['user_name']
            if user_name == 'user1':
                assert r['status'] == 'approved'
            else:
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        client.post('/session/logout')

        # -----------------------------------------
        # 3. User2 cancels reservation on resource1
        # -----------------------------------------
        operation += 1
        print(f"\n{operation}. User2 cancels reservation on resource1")

        client.post('/session/login', data=json.dumps({'name': 'user2', 'password': 'pass2'}), content_type='application/json')
        client.post('/reservation/cancel', data=json.dumps({'resource_id': resource1_id}), content_type='application/json')

        # Get updated reservations for resource1
        resp = client.get(f'/reservation/active?resource_id={resource1_id}')
        reservations1 = json.loads(resp.data)['reservations']

        print(f"Resource1 reservations after user2 cancel:")
        for r in reservations1:
            user_name = r['user_name']
            if user_name == 'user2':
                assert False, "User2 should not be in the reservations list"
            if user_name == 'user1':
                assert r['status'] == 'approved'
            elif user_name in ['user3', 'user4']:
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        # Get reservations for resource2 (should be unchanged)
        resp = client.get(f'/reservation/active?resource_id={resource2_id}')
        reservations2 = json.loads(resp.data)['reservations']

        print(f"Resource2 reservations (unchanged):")
        for r in reservations2:
            user_name = r['user_name']
            if user_name == 'user1':
                assert r['status'] == 'approved'
            else:
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")
        client.post('/session/logout')

        # -----------------------------------------
        # 4. User1 releases reservation on resource1
        # -----------------------------------------
        operation += 1
        print(f"\n{operation}. User1 releases reservation on resource1")

        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': 'pass1'}), content_type='application/json')
        client.post('/reservation/release', data=json.dumps({'resource_id': resource1_id}), content_type='application/json')

        # Get updated reservations for resource1
        resp = client.get(f'/reservation/active?resource_id={resource1_id}')
        reservations1 = json.loads(resp.data)['reservations']

        print(f"Resource1 reservations after user1 release:")
        for r in reservations1:
            user_name = r['user_name']
            if user_name == 'user1':
                assert False, "User1 should not be in the reservations list after release"
            elif user_name == 'user3':
                assert r['status'] == 'approved'  # Should be auto-approved
            elif user_name == 'user4':
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        # Get reservations for resource2 (should be unchanged)
        resp = client.get(f'/reservation/active?resource_id={resource2_id}')
        reservations2 = json.loads(resp.data)['reservations']

        print(f"Resource2 reservations (unchanged):")
        for r in reservations2:
            user_name = r['user_name']
            if user_name == 'user1':
                assert r['status'] == 'approved'
            else:
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        client.post('/session/logout')

        # ------------------------------------------
        # 5. User1 releases reservation on resource2
        # ------------------------------------------
        operation += 1
        print(f"\n{operation}. User1 releases reservation on resource2")

        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': 'pass1'}), content_type='application/json')
        client.post('/reservation/release', data=json.dumps({'resource_id': resource2_id}), content_type='application/json')

        # Get updated reservations for resource1
        resp = client.get(f'/reservation/active?resource_id={resource1_id}')
        reservations1 = json.loads(resp.data)['reservations']

        print(f"Resource1 reservations (unchanged):")
        for r in reservations1:
            user_name = r['user_name']
            if user_name == 'user3':
                assert r['status'] == 'approved'
            elif user_name == 'user4':
                assert r['status'] == 'requested'
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        # Get updated reservations for resource2
        resp = client.get(f'/reservation/active?resource_id={resource2_id}')
        reservations2 = json.loads(resp.data)['reservations']

        print(f"Resource2 reservations after user1 release:")
        for r in reservations2:
            user_name = r['user_name']
            if user_name == 'user1':
                assert False, "User1 should not be in the reservations list after release"
            elif user_name == 'user2':
                assert r['status'] == 'approved'  # Should be auto-approved
            print(f"  ID:{r['id']} User:{user_name} Status:{r['status']}")

        client.post('/session/logout')

    print(f"{GREEN}Endpoint reservation lifecycle tests passed!{RESET}\n")

def test_session_status():
    print("=== Session status endpoint tests started!")

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
                                   data=json.dumps({'name': 'admin', 'password': 'admin'}),
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
                   data=json.dumps({'name': 'testuser', 'email': 'test@example.com', 'password': 'pass123'}),
                   content_type='application/json')
        client.post('/session/logout')

        client.post('/session/login',
                   data=json.dumps({'name': 'testuser', 'password': 'pass123'}),
                   content_type='application/json')

        status_response = client.get('/session/status')
        assert status_response.status_code == 200
        data = json.loads(status_response.data)
        assert data['logged_in'] == True
        assert data['user_name'] == 'testuser'
        assert data['user_email'] == 'test@example.com'
        assert data['is_admin'] == False

    print(f"{GREEN}Session status tests passed!{RESET}\n")

def test_admin_user_modify():
    print("=== Admin user modify endpoint tests started!")

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
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': 'admin'}), content_type='application/json')
        resp = client.post('/admin/user/add', data=json.dumps({'name': 'testuser', 'email': 'test@example.com', 'password': 'pass123'}), content_type='application/json')
        user_id = json.loads(resp.data)['user_id']

        operation += 1
        print(f"\n{operation}. Admin modifies user email")
        response = client.post('/admin/user/modify', data=json.dumps({'user_id': user_id, 'email': 'newemail@example.com'}), content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User modified successfully'

        operation += 1
        print(f"\n{operation}. Admin modifies user password")
        response = client.post('/admin/user/modify', data=json.dumps({'user_id': user_id, 'password': 'newpass456'}), content_type='application/json')
        assert response.status_code == 200

        operation += 1
        print(f"\n{operation}. User modifies own data")
        client.post('/session/logout')
        client.post('/session/login', data=json.dumps({'name': 'testuser', 'password': 'newpass456'}), content_type='application/json')
        response = client.post('/admin/user/modify', data=json.dumps({'user_id': user_id, 'email': 'selfmodified@example.com'}), content_type='application/json')
        assert response.status_code == 200

        operation += 1
        print(f"\n{operation}. User cannot modify other user")
        client.post('/session/logout')
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': 'admin'}), content_type='application/json')
        resp2 = client.post('/admin/user/add', data=json.dumps({'name': 'user2', 'email': 'user2@example.com', 'password': 'pass2'}), content_type='application/json')
        user2_id = json.loads(resp2.data)['user_id']
        client.post('/session/logout')
        client.post('/session/login', data=json.dumps({'name': 'testuser', 'password': 'newpass456'}), content_type='application/json')
        response = client.post('/admin/user/modify', data=json.dumps({'user_id': user2_id, 'email': 'hacked@example.com'}), content_type='application/json')
        assert response.status_code == 403

        operation += 1
        print(f"\n{operation}. Missing user_id validation")
        response = client.post('/admin/user/modify', data=json.dumps({'email': 'test@example.com'}), content_type='application/json')
        assert response.status_code == 400

    print(f"{GREEN}Admin user modify tests passed!{RESET}\n")

if __name__ == "__main__":
    try:
        test_admin_user_add()
        test_admin_resource_add()
        test_admin_user_modify()
        test_endpoint_reservation_lifecycle()
        test_session_status()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise