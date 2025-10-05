# Import system modules for path manipulation
import sys
import os
import shutil
import logging
import time
import hashlib
from pathlib import Path

# Add parent directory to Python path so we can import our backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import our application classes
from backend.app.database import Database
from backend.app.application import ReserviaApp

# Color constants
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Test configuration constants - isolated from production
HOME = str(Path.home())
TEST_DIR_NAME = '.reservia_test_session'  # Separate test directory
TEST_APP_NAME = 'reservia_test_session'   # Test app name
TEST_DB_NAME = 'test_session.db'          # Test database file

def hash_password(password):
    """Hash password using SHA-256 (same as client-side)"""
    return hashlib.sha256(password.encode()).hexdigest()

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

    # CRITICAL: Reset the Database singleton instance
    # This ensures each test starts with a fresh database connection
    Database._instance = None

    # Small delay to ensure all resources are released
    time.sleep(0.1)

    # Get user's home directory
    test_path = os.path.join(HOME, TEST_DIR_NAME)

    # Remove entire test directory if it exists
    if os.path.exists(test_path):
        shutil.rmtree(test_path)  # Recursively delete directory and contents

def test_db_session_login_logout():
    print("=== Database session login/logout tests started!")
    
    # Start with clean slate - remove any existing test data
    cleanup_test_databases()

    # Configuration dictionary for test Flask app
    config_dict = {
        'app_name': TEST_APP_NAME,
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': TEST_DB_NAME},
    }

    # Create Flask app instance with session support
    app = ReserviaApp(config_dict)

    # CRITICAL: Flask sessions only work within request context
    # test_request_context() simulates an HTTP request environment
    with app.test_request_context():

        print("\nTesting initial session state...")
        print("  Getting database singleton instance...")
        db = Database.get_instance()

        print("  Verifying no user is logged in initially...")
        assert not db.is_logged_in()           # Should return False initially
        assert db.get_current_user() is None   # No user data in session

        print("\nTesting successful admin login...")
        print("  Attempting login with admin credentials...")
        success, user, error_code, error_msg = db.login("admin", hash_password("admin"))
        assert success and user is not None   # Login should succeed and return User object
        assert user.name == "admin"            # Verify user properties
        assert user.email == "admin@admin.se"

        print("  Verifying session state after login...")
        assert db.is_logged_in()               # Should now return True
        current_user = db.get_current_user()   # Should return user data from session
        assert current_user is not None
        assert current_user['user_name'] == "admin"     # Session stores user data as dict
        assert current_user['user_email'] == "admin@admin.se"

        print("\nTesting logout functionality...")
        print("  Attempting to logout...")
        success, data, error_code, error_msg = db.logout()
        assert success is True                 # Logout should succeed

        print("  Verifying session state after logout...")
        assert not db.is_logged_in()           # Should be False again
        assert db.get_current_user() is None   # Session should be cleared

    print("\nTesting logout when not logged in...")
    with app.test_request_context():
        print("  Attempting logout with no active session...")
        success, data, error_code, error_msg = db.logout()
        assert success is False                # Should return False (nothing to logout)

        print("\nTesting failed login...")
        print("  Attempting login with wrong password...")
        success, user, error_code, error_msg = db.login("admin", hash_password("wrongpassword"))
        assert not success and user is None   # Should fail and return None for failed login
        assert not db.is_logged_in()           # Should remain not logged in

    print(f"{GREEN}Database session login/logout tests passed!{RESET}")

if __name__ == "__main__":
    try:
        test_db_session_login_logout()
    except Exception as e:
        print(f"{RED}Tests failed: {e}{RESET}")
        raise