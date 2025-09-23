import sys
import os
import shutil
import logging
import time
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database
from backend.app.application import ReserviaApp
from backend.app.utils import get_current_epoch, epoch_to_iso8601

# Color constants
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Test configuration constants
HOME = str(Path.home())
TEST_DIR_NAME = '.reservia_test_request'
TEST_APP_NAME = 'reservia_test_request'
TEST_DB_NAME = 'test_request.db'

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

def test_db_create_request_for_resource():
    print("=== Database send request for resource tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        # Test request without login (should fail)
        print("\nTesting request without login...")
        result = db.create_request_for_resource(1)
        assert result is None

        # Login as admin to create user and resource
        print("  Logging in as admin...")
        admin_user = db.login("admin", "admin")
        assert admin_user is not None

        # Create a test user
        print("  Creating test user...")
        test_user = db.create_user("testuser", "test@example.com", "testpass123")
        assert test_user is not None

        # Create a resource
        print("  Creating test resource...")
        resource = db.create_resource("Test Resource", "A test resource for booking")
        assert resource is not None
        resource_id = resource.id

        # Logout admin and login as test user
        print("  Logging out admin and logging in as test user...")
        db.logout()
        logged_in_user = db.login("testuser", "testpass123")
        assert logged_in_user is not None

        # Test successful request
        print("\nTesting successful resource request...")
        request = db.create_request_for_resource(resource_id)
        assert request is not None
        assert request.user_id == test_user.id
        assert request.resource_id == resource_id
        assert request.request_date is not None
        assert request.approved_date is None
        assert request.cancelled_date is None

        # Test request for non-existent resource
        print("\nTesting request for non-existent resource...")
        result = db.create_request_for_resource(99999)
        assert result is None

        # Test time conversion methods
        print("\nTesting time conversion methods...")
        current_epoch = get_current_epoch()
        assert isinstance(current_epoch, int)

        iso_time = epoch_to_iso8601(current_epoch)
        assert isinstance(iso_time, str)
        assert "T" in iso_time  # ISO format contains T separator
        assert "+" in iso_time or "Z" in iso_time  # Should have timezone info

    print(f"{GREEN}Database send request for resource tests passed!{RESET}")

def test_db_update_request_for_resource():
    print("=== Database update request for resource tests started!")

    cleanup_test_databases()

    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME}
    }

    app = ReserviaApp(config_dict)

    with app.test_request_context():
        db = Database.get_instance(config_dict)

        # Setup test data
        print("\nSetting up test data...")
        print("  Logging in as admin...")
        admin_user = db.login("admin", "admin")
        assert admin_user is not None

        print("  Creating test user...")
        test_user = db.create_user("testuser", "test@example.com", "testpass123")
        assert test_user is not None

        print("  Creating test resource...")
        resource = db.create_resource("Test Resource", "A test resource for booking")
        assert resource is not None
        resource_id = resource.id

        print("  Logging out admin and logging in as test user...")
        db.logout()
        logged_in_user = db.login("testuser", "testpass123")
        assert logged_in_user is not None

        print("  Creating test requests...")
        request1 = db.create_request_for_resource(resource_id)
        request2 = db.create_request_for_resource(resource_id)
        request3 = db.create_request_for_resource(resource_id)
        request4 = db.create_request_for_resource(resource_id)
        assert request1 and request2 and request3 and request4

        print("  Logging out user...")
        db.logout()

        # Test update with approved_date only
        print("\nTesting update with approved_date only...")
        approved_time = get_current_epoch()
        result = db.update_request_for_resource(request1.id, approved_date=approved_time)
        assert result is not None
        assert result.approved_date == approved_time
        assert result.cancelled_date is None

        # Test update with cancelled_date only
        print("\nTesting update with cancelled_date only...")
        cancelled_time = get_current_epoch()
        result = db.update_request_for_resource(request2.id, cancelled_date=cancelled_time)
        assert result is not None
        assert result.cancelled_date == cancelled_time
        assert result.approved_date is None

        # Test update without any date
        print("\nTesting update without any date...")
        result = db.update_request_for_resource(request3.id)
        assert result is not None
        assert result.approved_date is None
        assert result.cancelled_date is None

        # Test update with both approved_date and cancelled_date
        print("\nTesting update with both approved_date and cancelled_date...")
        approved_time2 = get_current_epoch()
        cancelled_time2 = get_current_epoch()
        result = db.update_request_for_resource(request4.id, approved_date=approved_time2, cancelled_date=cancelled_time2)
        assert result is not None
        assert result.approved_date == approved_time2
        assert result.cancelled_date == cancelled_time2

        # Test update non-existent request
        print("\nTesting update of non-existent request...")
        result = db.update_request_for_resource(99999)
        assert result is None

    print(f"{GREEN}Database update request for resource tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_create_request_for_resource()
        test_db_update_request_for_resource()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise