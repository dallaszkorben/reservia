import sys
import os
import shutil
import logging
import time
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database, ReservationLifecycle
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


def test_db_request_reservation_failure():
    print("=== Database request reservation failure tests started!")

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
        success, admin_user, _, _ = db.login("admin", "admin")
        assert success and admin_user is not None

        print("  Creating test user...")
        success, test_user, _, _ = db.create_user("testuser", "test@example.com", "testpass123")
        assert success and test_user is not None

        print("  Creating test resource...")
        success, resource, _, _ = db.create_resource("Test Resource", "A test resource for booking")
        assert success and resource is not None
        resource_id = resource.id

        print("  Logging out admin and logging in as test user...")
        db.logout()
        success, logged_in_user, _, _ = db.login("testuser", "testpass123")
        assert success and logged_in_user is not None

        print("  Emptying reservation_lifecycle table...")
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        # Test first request (should succeed)
        print("\nTesting first reservation request...")
        print("  Making first reservation request...")
        success, first_reservation, _, _ = db.request_reservation(resource_id)
        assert success and first_reservation is not None
        assert first_reservation.user_id == test_user.id
        assert first_reservation.resource_id == resource_id
        assert first_reservation.request_date is not None
        assert first_reservation.approved_date is not None  # Should be auto-approved

        # Test second request (should fail)
        print("\nTesting duplicate reservation request...")
        print("  Making second reservation request (should fail)...")
        success, second_reservation, error_code, _ = db.request_reservation(resource_id)
        assert not success and second_reservation is None and error_code == "DUPLICATE_RESERVATION"

    print(f"{GREEN}Database request reservation failure tests passed!{RESET}\n")

def test_db_cancel_reservation_empty_table():
    print("=== Database cancel reservation on empty table tests started!")

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
        success, admin_user, _, _ = db.login("admin", "admin")
        assert success and admin_user is not None

        print("  Creating test user...")
        success, test_user, _, _ = db.create_user("testuser", "test@example.com", "testpass123")
        assert success and test_user is not None

        print("  Creating test resource...")
        success, resource, _, _ = db.create_resource("Test Resource", "A test resource for booking")
        assert success and resource is not None
        resource_id = resource.id

        print("  Logging out admin and logging in as test user...")
        db.logout()
        success, logged_in_user, _, _ = db.login("testuser", "testpass123")
        assert success and logged_in_user is not None

        print("  Emptying reservation_lifecycle table...")
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        # Test cancel on empty table (should fail)
        print("\nTesting cancel reservation on empty table...")
        print("  Attempting to cancel reservation (should fail)...")
        success, result, error_code, _ = db.cancel_reservation(resource_id)
        assert not success and result is None and error_code == "RESERVATION_NOT_FOUND"

    print(f"{GREEN}Database cancel reservation on empty table tests passed!{RESET}\n")

def test_db_release_reservation_empty_table():
    print("=== Database release reservation on empty table tests started!")

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
        success, admin_user, _, _ = db.login("admin", "admin")
        assert success and admin_user is not None

        print("  Creating test user...")
        success, test_user, _, _ = db.create_user("testuser", "test@example.com", "testpass123")
        assert success and test_user is not None

        print("  Creating test resource...")
        success, resource, _, _ = db.create_resource("Test Resource", "A test resource for booking")
        assert success and resource is not None
        resource_id = resource.id

        print("  Logging out admin and logging in as test user...")
        db.logout()
        success, logged_in_user, _, _ = db.login("testuser", "testpass123")
        assert success and logged_in_user is not None

        print("  Emptying reservation_lifecycle table...")
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        # Test release on empty table (should fail)
        print("\nTesting release reservation on empty table...")
        print("  Attempting to release reservation (should fail)...")
        success, result, error_code, _ = db.release_reservation(resource_id)
        assert not success and result is None and error_code == "RESERVATION_NOT_FOUND"

    print(f"{GREEN}Database release reservation on empty table tests passed!{RESET}\n")

def test_db_reservation_lifecycle_workflow_1():
    print("=== Database reservation lifecycle workflow tests started!")

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
        operation = 0

        # 0. Empty table and setup
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        _, admin_user, _, _ = db.login("admin", "admin")
        _, resource1, _, _ = db.create_resource("Resource1", "Test resource 1")
        resource1_id = resource1.id

        _, user1, _, _ = db.create_user("user1", "user1@example.com", "pass1")
        _, user2, _, _ = db.create_user("user2", "user2@example.com", "pass2")
        _, user3, _, _ = db.create_user("user3", "user3@example.com", "pass3")
        _, user4, _, _ = db.create_user("user4", "user4@example.com", "pass4")

        operation += 1

        # -----------------------------
        # 1. User1 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user1", "pass1")
        _, result, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user1 reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # -----------------------------
        # 2. User4 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user4", "pass4")
        _, result, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user4 reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user4.id:  # User4's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # -----------------------------
        # 3. User2 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user2", "pass2")
        _, result, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user2 reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user4.id:  # User4's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:  # User2's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # ----------------------------
        # 4. User2 cancels reservation
        # ----------------------------
        _, _, _, _ = db.cancel_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user2 cancel:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user4.id:  # User4's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:  # User2's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is not None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # -----------------------------
        # 5. User3 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user3", "pass3")
        _, result, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user3 reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user4.id:  # User4's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:  # User2's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is not None
                assert r.released_date is None
            elif r.user_id == user3.id:  # User3's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # -----------------------------
        # 6. User1 releases reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user1", "pass1")
        _, _, _, _ = db.release_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user1 release:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is not None
            elif r.user_id == user4.id:  # User4's record (should be auto-approved)
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:  # User2's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is not None
                assert r.released_date is None
            elif r.user_id == user3.id:  # User3's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        #print("")
        operation += 1

    print(f"{GREEN}Database release reservation on empty table tests passed!{RESET}\n")

def test_db_reservation_lifecycle_workflow_2():
    print("=== Database reservation lifecycle workflow 2 tests started!")

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
        operation = 0

        # 0. Empty table and setup
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        _, admin_user, _, _ = db.login("admin", "admin")
        _, resource1, _, _ = db.create_resource("Resource1", "Test resource 1")
        resource1_id = resource1.id

        _, user1, _, _ = db.create_user("user1", "user1@example.com", "pass1")
        _, user2, _, _ = db.create_user("user2", "user2@example.com", "pass2")
        _, user3, _, _ = db.create_user("user3", "user3@example.com", "pass3")
        _, user4, _, _ = db.create_user("user4", "user4@example.com", "pass4")

        operation += 1

        # -----------------------------
        # 1. User1 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user1", "pass1")
        _, result1, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user1 reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # -----------------------------
        # 2. User2 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user2", "pass2")
        _, result2, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user2 reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:  # User2's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # -----------------------------
        # 3. User3 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user3", "pass3")
        _, result3, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user3 reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:  # User2's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user3.id:  # User3's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # ----------------------------
        # 4. User2 cancels reservation
        # ----------------------------
        db.logout()
        _, _, _, _ = db.login("user2", "pass2")
        _, _, _, _ = db.cancel_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user2 cancel:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:  # User2's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is not None
                assert r.released_date is None
            elif r.user_id == user3.id:  # User3's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

        # Wait to ensure different timestamp
        time.sleep(1)

        # -----------------------------
        # 5. User2 requests reservation
        # -----------------------------
        db.logout()
        _, _, _, _ = db.login("user2", "pass2")
        _, result4, _, _ = db.request_reservation(resource1_id)

        records = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.request_date).all()
        print(f"{operation}. After user2 new reservation:")
        for r in records:
            if r.user_id == user1.id:  # User1's record
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id and r.cancelled_date is None:  # User2's new record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user3.id:  # User3's record
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1

    print(f"{GREEN}Database reservation lifecycle workflow 2 tests passed!{RESET}")

def test_db_reservation_lifecycle_workflow_3():
    print("=== Database reservation lifecycle workflow 3 tests started!")

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
        operation = 0

        # 0. Empty table and setup
        db.session.query(ReservationLifecycle).delete()
        db.session.commit()

        _, admin_user, _, _ = db.login("admin", "admin")
        _, resource1, _, _ = db.create_resource("Resource1", "Test resource 1")
        resource1_id = resource1.id

        _, user1, _, _ = db.create_user("user1", "user1@example.com", "pass1")
        _, user2, _, _ = db.create_user("user2", "user2@example.com", "pass2")
        _, user3, _, _ = db.create_user("user3", "user3@example.com", "pass3")
        _, user4, _, _ = db.create_user("user4", "user4@example.com", "pass4")

        operation += 1

        # -----------------------------------
        # 1. User1/2/3/4 requests reservation
        # -----------------------------------
        db.logout()
        _, _, _, _ = db.login("user1", "pass1")
        _, result1, _, _ = db.request_reservation(resource1_id)

        db.logout()
        _, _, _, _ = db.login("user2", "pass2")
        _, result1, _, _ = db.request_reservation(resource1_id)

        db.logout()
        _, _, _, _ = db.login("user3", "pass3")
        _, result1, _, _ = db.request_reservation(resource1_id)

        db.logout()
        _, _, _, _ = db.login("user4", "pass4")
        _, result1, _, _ = db.request_reservation(resource1_id)

        active_reservations = db.get_active_reservations(resource1_id)

        print(f"{operation}. user1/user2/user3/user4 requested reservations:")
        for r in active_reservations:
            if r.user_id == user1.id:
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user2.id:
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user3.id:
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user4.id:
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        print("")
        operation += 1
        time.sleep(1)

        # --------------------------------------
        # 2. Release User1/2 release reservation
        # --------------------------------------
        db.logout()
        _, _, _, _ = db.login("user1", "pass1")
        _, result2, _, _ = db.release_reservation(resource1_id)

        db.logout()
        _, _, _, _ = db.login("user2", "pass2")
        _, result2, _, _ = db.release_reservation(resource1_id)

        active_reservations = db.get_active_reservations(resource1_id)

        print(f"{operation}. user1 and after user2 released their reservations:")
        for r in active_reservations:
            if r.user_id == user1.id:  # User1's record
                assert False, "The user1 released the resource, but it is still in the active reservation list"
            elif r.user_id == user2.id:
                assert False, "The user2 released the resource, but it is still in the active reservation list"
            elif r.user_id == user3.id:
                assert r.request_date is not None
                assert r.approved_date is not None
                assert r.cancelled_date is None
                assert r.released_date is None
            elif r.user_id == user4.id:
                assert r.request_date is not None
                assert r.approved_date is None
                assert r.cancelled_date is None
                assert r.released_date is None
            print(f"  ID:{r.id} User:{r.user_id}({r.user.name}) Resource:{r.resource_id} Request:{r.request_date} Approved:{r.approved_date} Cancelled:{r.cancelled_date} Released:{r.released_date}")
        #print("")
        operation += 1

    print(f"{GREEN}Database reservation lifecycle workflow 2 tests passed!{RESET}")


if __name__ == "__main__":
    try:
        test_db_request_reservation_failure()
        test_db_cancel_reservation_empty_table()
        test_db_release_reservation_empty_table()
        test_db_reservation_lifecycle_workflow_1()
        test_db_reservation_lifecycle_workflow_2()
        test_db_reservation_lifecycle_workflow_3()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise
        # Wait to ensure different timestamp
        time.sleep(1)
