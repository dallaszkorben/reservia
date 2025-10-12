#!/usr/bin/env python3
"""
Simple test to verify automatic reservation expiration functionality.
"""

import sys
import os
import time
import hashlib
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import Database
from backend.app.application import ReserviaApp

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def test_expiration():
    print("=== Testing Automatic Reservation Expiration ===")
    
    # Setup test config with very short expiration time
    config_dict = {
        'app_name': 'reservia_expiration_test',
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'INFO', 'backupCount': 1},
        'database': {'name': 'test_expiration.db'}
    }
    
    # Temporarily override config for fast testing
    from backend.config.config import CONFIG
    original_keep_alive = CONFIG['approved_keep_alive_sec']
    original_check_interval = CONFIG['expiration_check_interval_sec']
    
    CONFIG['approved_keep_alive_sec'] = 3  # 3 seconds expiration
    CONFIG['expiration_check_interval_sec'] = 1  # Check every 1 second
    
    try:
        app = ReserviaApp(config_dict)
        
        with app.test_request_context():
            db = Database.get_instance(config_dict)
            
            print("1. Setting up test data...")
            # Login as admin and create test user and resource
            success, _, _, _ = db.login("admin", hash_password("admin"))
            assert success
            
            success, user, _, _ = db.create_user("testuser", "test@example.com", hash_password("testpass"))
            assert success
            user_id = user.id
            
            success, resource, _, _ = db.create_resource("Test Resource", "Test resource for expiration")
            assert success
            resource_id = resource.id
            
            db.logout()
            
            print("2. User makes reservation...")
            # Login as test user and make reservation
            success, _, _, _ = db.login("testuser", hash_password("testpass"))
            assert success
            
            success, reservation, _, _ = db.request_reservation(resource_id)
            assert success
            assert reservation.approved_date is not None  # Should be auto-approved
            print(f"   Reservation approved with 3-second expiration")
            
            print("3. Waiting for expiration (4 seconds)...")
            time.sleep(4)  # Wait longer than expiration time
            
            print("4. Checking if reservation was auto-expired...")
            reservations = db.get_active_reservations(resource_id)
            
            if len(reservations) == 0:
                print("   ✅ SUCCESS: Reservation was automatically expired and released!")
            else:
                print("   ❌ FAILED: Reservation still active after expiration time")
                for r in reservations:
                    print(f"      Reservation {r.id}: User {r.user.name}, Released: {r.released_date}")
            
            print("5. Testing queue auto-approval after expiration...")
            # Create second user and reservation
            db.logout()
            success, _, _, _ = db.login("admin", hash_password("admin"))
            success, user2, _, _ = db.create_user("testuser2", "test2@example.com", hash_password("testpass2"))
            assert success
            user2_id = user2.id
            db.logout()
            
            # First user makes reservation again
            success, _, _, _ = db.login("testuser", hash_password("testpass"))
            success, reservation1, _, _ = db.request_reservation(resource_id)
            assert success and reservation1.approved_date is not None
            
            # Second user makes reservation (should be queued)
            db.logout()
            success, _, _, _ = db.login("testuser2", hash_password("testpass2"))
            success, reservation2, _, _ = db.request_reservation(resource_id)
            assert success and reservation2.approved_date is None  # Should be queued
            print("   Second user queued behind first user")
            
            print("6. Waiting for first reservation to expire and second to be auto-approved...")
            time.sleep(4)  # Wait for expiration
            
            reservations = db.get_active_reservations(resource_id)
            if len(reservations) == 1 and reservations[0].user_id == user2_id and reservations[0].approved_date is not None:
                print("   ✅ SUCCESS: Second user was automatically approved after first expired!")
            else:
                print("   ❌ FAILED: Queue auto-approval after expiration didn't work correctly")
                for r in reservations:
                    status = "approved" if r.approved_date else "queued"
                    print(f"      Reservation {r.id}: User {r.user.name} ({status})")
    
    finally:
        # Restore original config
        CONFIG['approved_keep_alive_sec'] = original_keep_alive
        CONFIG['expiration_check_interval_sec'] = original_check_interval
        
        # Cleanup
        home = str(Path.home())
        test_dir = os.path.join(home, '.reservia_expiration_test')
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
    
    print("=== Expiration Test Complete ===")

if __name__ == "__main__":
    test_expiration()