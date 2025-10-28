"""
Reservation System Test Suite

Comprehensive test suite for reservation system functionality, covering:
- Database reservation operations (request, cancel, release, get_active)
- API endpoints for reservations (/reservation/request, /reservation/cancel, /reservation/release, /reservation/active)
- Queue management and auto-approval logic
- Complex multi-user reservation workflows
- Reservation state transitions and validation

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

from backend.app.database import Database, ReservationLifecycle
from backend.app.application import ReserviaApp

# Color constants
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Test configuration constants
HOME = str(Path.home())
TEST_DIR_NAME = '.reservia_test_reservations'
TEST_APP_NAME = 'reservia_test_reservations'
TEST_DB_NAME = 'test_reservations.db'

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

# === Database Layer Tests ===

def test_db_reservation_request_failure():
    """
    Test database reservation request failure scenarios including duplicate reservations
    and proper error handling for already reserved resources.
    """
    print("=== Database reservation request failure tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)
        operation = 0

        operation += 1
        print(f"\n{operation}. Setup test data")
        success, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert success and admin_user is not None
        success, test_user, _, _ = db.create_user("testuser", "test@example.com", hash_password("testpass123"))
        assert success and test_user is not None
        success, resource, _, _ = db.create_resource("Test Resource", "A test resource for booking")
        assert success and resource is not None
        resource_id = resource.id
        db.logout()
        success, logged_in_user, _, _ = db.login("testuser", hash_password("testpass123"))
        assert success and logged_in_user is not None
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        operation += 1
        print(f"\n{operation}. First reservation request test")
        success, first_reservation, _, _ = db.request_reservation(resource_id)
        assert success and first_reservation is not None
        assert first_reservation.user_id == test_user.id
        assert first_reservation.resource_id == resource_id
        assert first_reservation.request_date is not None
        assert first_reservation.approved_date is not None

        operation += 1
        print(f"\n{operation}. Duplicate reservation request test")
        success, second_reservation, error_code, _ = db.request_reservation(resource_id)
        assert not success and second_reservation is None and error_code == "DUPLICATE_RESERVATION"

    print(f"{GREEN}Database reservation request failure tests passed!{RESET}")

def test_db_reservation_empty_table_operations():
    """
    Test reservation operations on empty tables to verify proper error handling
    when no reservations exist.
    """
    print("=== Database reservation empty table operations tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)
        operation = 0

        operation += 1
        print(f"\n{operation}. Setup test data")
        success, admin_user, _, _ = db.login("admin", hash_password("admin"))
        assert success and admin_user is not None
        success, test_user, _, _ = db.create_user("testuser", "test@example.com", hash_password("testpass123"))
        assert success and test_user is not None
        success, resource, _, _ = db.create_resource("Test Resource", "A test resource for booking")
        assert success and resource is not None
        resource_id = resource.id
        db.logout()
        success, logged_in_user, _, _ = db.login("testuser", hash_password("testpass123"))
        assert success and logged_in_user is not None
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        operation += 1
        print(f"\n{operation}. Cancel reservation on empty table test")
        success, result, error_code, _ = db.cancel_reservation(resource_id, test_user.id)
        assert not success and result is None and error_code == "RESERVATION_NOT_FOUND"

        operation += 1
        print(f"\n{operation}. Release reservation on empty table test")
        success, result, error_code, _ = db.release_reservation(resource_id, test_user.id)
        assert not success and result is None and error_code == "RESERVATION_NOT_FOUND"

    print(f"{GREEN}Database reservation empty table operations tests passed!{RESET}")

def test_db_reservation_lifecycle_workflow():
    """
    Test complex database reservation workflow with multiple users including
    requests, cancellations, releases, and auto-approval logic.
    """
    print("=== Database reservation lifecycle workflow tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)
        operation = 0

        # Setup
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        _, admin_user, _, _ = db.login("admin", hash_password("admin"))
        _, resource1, _, _ = db.create_resource("Resource1", "Test resource 1")
        resource1_id = resource1.id

        _, user1, _, _ = db.create_user("user1", "user1@example.com", hash_password("pass1"))
        _, user2, _, _ = db.create_user("user2", "user2@example.com", hash_password("pass2"))
        _, user3, _, _ = db.create_user("user3", "user3@example.com", hash_password("pass3"))
        _, user4, _, _ = db.create_user("user4", "user4@example.com", hash_password("pass4"))

        operation += 1
        print(f"\n{operation}. Multiple users request same resource")
        
        # User1 requests (should be auto-approved)
        db.logout()
        _, _, _, _ = db.login("user1", hash_password("pass1"))
        _, result, _, _ = db.request_reservation(resource1_id)

        # User2 requests (should be queued)
        db.logout()
        _, _, _, _ = db.login("user2", hash_password("pass2"))
        _, result, _, _ = db.request_reservation(resource1_id)

        # User3 requests (should be queued)
        db.logout()
        _, _, _, _ = db.login("user3", hash_password("pass3"))
        _, result, _, _ = db.request_reservation(resource1_id)

        active_reservations = db.get_active_reservations(resource1_id)
        print(f"Active reservations after all requests:")
        for r in active_reservations:
            status = "approved" if r.approved_date else "requested"
            print(f"  User: {r.user.name}, Status: {status}")
            
            if r.user_id == user1.id:
                assert r.approved_date is not None  # Should be approved
            else:
                assert r.approved_date is None  # Should be queued

        operation += 1
        print(f"\n{operation}. User1 releases resource, User2 should be auto-approved")
        
        db.logout()
        _, _, _, _ = db.login("user1", hash_password("pass1"))
        _, _, _, _ = db.release_reservation(resource1_id, user1.id)

        active_reservations = db.get_active_reservations(resource1_id)
        print(f"Active reservations after User1 release:")
        for r in active_reservations:
            status = "approved" if r.approved_date else "requested"
            print(f"  User: {r.user.name}, Status: {status}")
            
            if r.user_id == user2.id:
                assert r.approved_date is not None  # Should be auto-approved
            elif r.user_id == user3.id:
                assert r.approved_date is None  # Should still be queued

        operation += 1
        print(f"\n{operation}. User3 cancels reservation")
        
        db.logout()
        _, _, _, _ = db.login("user3", hash_password("pass3"))
        _, _, _, _ = db.cancel_reservation(resource1_id, user3.id)

        active_reservations = db.get_active_reservations(resource1_id)
        print(f"Active reservations after User3 cancel:")
        for r in active_reservations:
            status = "approved" if r.approved_date else "requested"
            print(f"  User: {r.user.name}, Status: {status}")
            
            # User3 should not be in active reservations anymore
            assert r.user_id != user3.id

    print(f"{GREEN}Database reservation lifecycle workflow tests passed!{RESET}")

# === API Endpoint Tests ===

def test_api_reservation_request():
    """
    Test /reservation/request endpoint functionality including successful requests,
    queue management, and authorization checks.
    """
    print("=== API reservation request endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        # Setup
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user1', 'email': 'user1@example.com', 'password': hash_password('pass1')}), content_type='application/json')
        resp = client.post('/admin/resource/add', data=json.dumps({'name': 'Test Resource', 'comment': 'Test resource'}), content_type='application/json')
        resource_id = json.loads(resp.data)['resource_id']
        client.post('/session/logout')

        operation += 1
        print(f"\n{operation}. Unauthorized reservation request test")
        response = client.post('/reservation/request', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        assert response.status_code == 401

        operation += 1
        print(f"\n{operation}. Successful reservation request test")
        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': hash_password('pass1')}), content_type='application/json')
        response = client.post('/reservation/request', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Reservation request successful'
        assert data['status'] == 'approved'

        operation += 1
        print(f"\n{operation}. Duplicate reservation request test")
        response = client.post('/reservation/request', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data

    print(f"{GREEN}API reservation request tests passed!{RESET}")

def test_api_reservation_lifecycle():
    """
    Test complete reservation lifecycle through API endpoints including
    multiple user requests, queue management, cancellations, and releases.
    """
    print("=== API reservation lifecycle tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        # Setup: Create users and resources
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')

        client.post('/admin/user/add', data=json.dumps({'name': 'user1', 'email': 'user1@example.com', 'password': hash_password('pass1')}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user2', 'email': 'user2@example.com', 'password': hash_password('pass2')}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user3', 'email': 'user3@example.com', 'password': hash_password('pass3')}), content_type='application/json')

        resp1 = client.post('/admin/resource/add', data=json.dumps({'name': 'resource1', 'comment': 'Test resource 1'}), content_type='application/json')
        resource1_id = json.loads(resp1.data)['resource_id']

        client.post('/session/logout')

        operation += 1
        print(f"\n{operation}. Multiple reservation requests")

        # User1-3 request resource1
        for user in ['user1', 'user2', 'user3']:
            client.post('/session/login', data=json.dumps({'name': user, 'password': hash_password(f'pass{user[-1]}')}), content_type='application/json')
            client.post('/reservation/request', data=json.dumps({'resource_id': resource1_id}), content_type='application/json')
            client.post('/session/logout')

        # Check reservations
        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': hash_password('pass1')}), content_type='application/json')
        resp = client.get(f'/reservation/active?resource_id={resource1_id}')
        reservations = json.loads(resp.data)['reservations']

        print(f"Reservations after all requests:")
        for r in reservations:
            user_name = r['user_name']
            status = r['status']
            print(f"  User: {user_name}, Status: {status}")
            
            if user_name == 'user1':
                assert status == 'approved'
            else:
                assert status == 'requested'

        client.post('/session/logout')

        operation += 1
        print(f"\n{operation}. User1 releases reservation")

        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': hash_password('pass1')}), content_type='application/json')
        client.post('/reservation/release', data=json.dumps({'resource_id': resource1_id}), content_type='application/json')

        # Check updated reservations
        resp = client.get(f'/reservation/active?resource_id={resource1_id}')
        reservations = json.loads(resp.data)['reservations']

        print(f"Reservations after user1 release:")
        for r in reservations:
            user_name = r['user_name']
            status = r['status']
            print(f"  User: {user_name}, Status: {status}")
            
            if user_name == 'user1':
                assert False, "User1 should not be in active reservations after release"
            elif user_name == 'user2':
                assert status == 'approved'  # Should be auto-approved
            elif user_name == 'user3':
                assert status == 'requested'

        client.post('/session/logout')

    print(f"{GREEN}API reservation lifecycle tests passed!{RESET}")

def test_api_reservation_active():
    """
    Test /reservation/active endpoint functionality including proper filtering
    and authorization checks.
    """
    print("=== API reservation active endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        # Setup
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user1', 'email': 'user1@example.com', 'password': hash_password('pass1')}), content_type='application/json')
        resp = client.post('/admin/resource/add', data=json.dumps({'name': 'Test Resource', 'comment': 'Test resource'}), content_type='application/json')
        resource_id = json.loads(resp.data)['resource_id']
        client.post('/session/logout')

        operation += 1
        print(f"\n{operation}. Unauthorized access test")
        response = client.get(f'/reservation/active?resource_id={resource_id}')
        assert response.status_code == 401

        operation += 1
        print(f"\n{operation}. Get active reservations test")
        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': hash_password('pass1')}), content_type='application/json')
        client.post('/reservation/request', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        
        response = client.get(f'/reservation/active?resource_id={resource_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Active reservations retrieved successfully'
        assert 'reservations' in data
        assert data['count'] == 1

    print(f"{GREEN}API reservation active tests passed!{RESET}")

def test_api_reservation_keep_alive():
    """
    Test /reservation/keep_alive endpoint functionality including successful
    keep alive operations, authorization checks, and error handling.
    """
    print("=== API reservation keep_alive endpoint tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'data_dir': os.path.join(HOME, TEST_DIR_NAME),
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
        'data_dir': os.path.join(HOME, TEST_DIR_NAME)
    }

    app = ReserviaApp(config_dict)
    operation = 0

    with app.test_client() as client:
        # Setup
        client.post('/session/login', data=json.dumps({'name': 'admin', 'password': hash_password('admin')}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user1', 'email': 'user1@example.com', 'password': hash_password('pass1')}), content_type='application/json')
        client.post('/admin/user/add', data=json.dumps({'name': 'user2', 'email': 'user2@example.com', 'password': hash_password('pass2')}), content_type='application/json')
        resp = client.post('/admin/resource/add', data=json.dumps({'name': 'Test Resource', 'comment': 'Test resource'}), content_type='application/json')
        resource_id = json.loads(resp.data)['resource_id']
        client.post('/session/logout')

        operation += 1
        print(f"\n{operation}. Unauthorized keep_alive test")
        # Test: Verify that unauthenticated users cannot access keep_alive endpoint
        response = client.post('/reservation/keep_alive', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        assert response.status_code == 401  # Should return 401 Unauthorized

        operation += 1
        print(f"\n{operation}. Keep_alive without reservation test")
        # Test: Verify that users cannot keep_alive when they have no approved reservation
        client.post('/session/login', data=json.dumps({'name': 'user1', 'password': hash_password('pass1')}), content_type='application/json')
        response = client.post('/reservation/keep_alive', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        assert response.status_code == 404  # Should return 404 Not Found
        data = json.loads(response.data)
        assert 'error' in data  # Should contain error message

        operation += 1
        print(f"\n{operation}. Successful keep_alive test")
        # Test: Verify successful keep_alive operation updates valid_until_date
        # First make a reservation
        client.post('/reservation/request', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        
        # Get initial valid_until_date
        with app.test_request_context():
            db = Database.get_instance(config_dict)
            reservations = db.get_active_reservations(resource_id)
            initial_valid_until = reservations[0].valid_until_date
        
        # Wait a moment to ensure time difference
        time.sleep(1)
        
        # Keep alive the reservation
        response = client.post('/reservation/keep_alive', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        assert response.status_code == 200  # Should return 200 OK
        data = json.loads(response.data)
        assert data['message'] == 'Reservation kept alive successfully'  # Should return success message
        assert 'valid_until_date' in data  # Should include updated valid_until_date
        
        # Verify valid_until_date was updated to a later time
        with app.test_request_context():
            db = Database.get_instance(config_dict)
            reservations = db.get_active_reservations(resource_id)
            new_valid_until = reservations[0].valid_until_date
            assert new_valid_until > initial_valid_until  # New time should be later than initial

        operation += 1
        print(f"\n{operation}. Keep_alive queued reservation test")
        # Test: Verify that users CAN keep_alive queued (non-approved) reservations when requested_keep_alive_sec > 0
        # User2 makes a request (should be queued since user1 has approved reservation)
        client.post('/session/logout')
        client.post('/session/login', data=json.dumps({'name': 'user2', 'password': hash_password('pass2')}), content_type='application/json')
        client.post('/reservation/request', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        
        # Try to keep alive queued reservation (should succeed since requested_keep_alive_sec = 1800 > 0)
        response = client.post('/reservation/keep_alive', data=json.dumps({'resource_id': resource_id}), content_type='application/json')
        assert response.status_code == 200  # Should return 200 OK
        data = json.loads(response.data)
        assert data['message'] == 'Reservation kept alive successfully'  # Should return success message
        assert 'valid_until_date' in data  # Should include updated valid_until_date

    print(f"{GREEN}API reservation keep_alive tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_reservation_request_failure()
        test_db_reservation_empty_table_operations()
        test_db_reservation_lifecycle_workflow()
        test_api_reservation_request()
        test_api_reservation_lifecycle()
        test_api_reservation_active()
        test_api_reservation_keep_alive()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise