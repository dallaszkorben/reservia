#!/usr/bin/env python3
"""
Test suite for automatic reservation expiration functionality.
Tests both database operations and background expiration thread behavior.
"""

import sys
import os
import time
import hashlib
import unittest
import shutil
from pathlib import Path

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.database import Database
from backend.app.application import ReserviaApp

class TestExpirationSystem(unittest.TestCase):
    """Test automatic reservation expiration and queue management."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.cleanup_test_databases()
        
        self.config_dict = {
            'app_name': 'reservia_expiration_test',
            'version': '1.0.0',

            'data_dir': os.path.join(str(Path.home()), '.reservia_expiration_test'),
            'log': {'log_name': 'test.log', 'level': 'INFO', 'backupCount': 1},
            'database': {'name': 'test_expiration.db'}
        }
        
        # Override config for fast testing
        from backend.config.config import CONFIG
        self.original_keep_alive = CONFIG['approved_keep_alive_sec']
        self.original_check_interval = CONFIG['expiration_check_interval_sec']
        
        CONFIG['approved_keep_alive_sec'] = 3  # 3 seconds expiration
        CONFIG['expiration_check_interval_sec'] = 1  # Check every 1 second
        
        self.app = ReserviaApp(self.config_dict)
    
    def tearDown(self):
        """Clean up after each test."""
        # Restore original config
        from backend.config.config import CONFIG
        CONFIG['approved_keep_alive_sec'] = self.original_keep_alive
        CONFIG['expiration_check_interval_sec'] = self.original_check_interval
        
        self.cleanup_test_databases()
    
    def cleanup_test_databases(self):
        """Clean up test database files and reset singleton."""
        if Database._instance is not None:
            try:
                Database._instance.session.close()
                Database._instance.engine.dispose()
            except:
                pass
        Database._instance = None
        
        test_path = os.path.join(str(Path.home()), '.reservia_expiration_test')
        if os.path.exists(test_path):
            shutil.rmtree(test_path)
    
    def hash_password(self, password):
        """Hash password for testing."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def test_automatic_reservation_expiration(self):
        """Test that approved reservations automatically expire after timeout."""
        with self.app.test_request_context():
            db = Database.get_instance(self.config_dict)
            
            # Setup test data
            success, _, _, _ = db.login("admin", self.hash_password("admin"))
            self.assertTrue(success)
            
            success, user, _, _ = db.create_user("testuser", "test@example.com", self.hash_password("testpass"))
            self.assertTrue(success)
            user_id = user.id
            
            success, resource, _, _ = db.create_resource("Test Resource", "Test resource for expiration")
            self.assertTrue(success)
            resource_id = resource.id
            
            db.logout()
            
            # User makes reservation
            success, _, _, _ = db.login("testuser", self.hash_password("testpass"))
            self.assertTrue(success)
            
            success, reservation, _, _ = db.request_reservation(resource_id)
            self.assertTrue(success)
            self.assertIsNotNone(reservation.approved_date)  # Should be auto-approved
            
            # Wait for expiration
            time.sleep(4)  # Wait longer than expiration time
            
            # Check if reservation was auto-expired
            reservations = db.get_active_reservations(resource_id)
            self.assertEqual(len(reservations), 0, "Reservation should have been automatically expired")
    
    def test_queue_auto_approval_after_expiration(self):
        """Test that queued users are automatically approved when current reservation expires."""
        with self.app.test_request_context():
            db = Database.get_instance(self.config_dict)
            
            # Setup test data
            success, _, _, _ = db.login("admin", self.hash_password("admin"))
            self.assertTrue(success)
            
            success, user1, _, _ = db.create_user("testuser1", "test1@example.com", self.hash_password("testpass1"))
            self.assertTrue(success)
            user1_id = user1.id
            
            success, user2, _, _ = db.create_user("testuser2", "test2@example.com", self.hash_password("testpass2"))
            self.assertTrue(success)
            user2_id = user2.id
            
            success, resource, _, _ = db.create_resource("Test Resource", "Test resource for queue testing")
            self.assertTrue(success)
            resource_id = resource.id
            
            db.logout()
            
            # First user makes reservation
            success, _, _, _ = db.login("testuser1", self.hash_password("testpass1"))
            self.assertTrue(success)
            success, reservation1, _, _ = db.request_reservation(resource_id)
            self.assertTrue(success)
            self.assertIsNotNone(reservation1.approved_date)
            
            # Second user makes reservation (should be queued)
            db.logout()
            success, _, _, _ = db.login("testuser2", self.hash_password("testpass2"))
            self.assertTrue(success)
            success, reservation2, _, _ = db.request_reservation(resource_id)
            self.assertTrue(success)
            self.assertIsNone(reservation2.approved_date)  # Should be queued
            
            # Wait for first reservation to expire
            time.sleep(4)
            
            # Check that second user was automatically approved
            reservations = db.get_active_reservations(resource_id)
            self.assertEqual(len(reservations), 1, "Should have exactly one active reservation")
            self.assertEqual(reservations[0].user_id, user2_id, "Second user should be approved")
            self.assertIsNotNone(reservations[0].approved_date, "Second user should have approved_date set")

if __name__ == "__main__":
    unittest.main()