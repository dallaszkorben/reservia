#!/usr/bin/env python3
"""
Test suite for reservia_integration.py script

Tests the integration script functionality including:
- Utility functions (get_username, check_no_auth_mode)
- Authentication and session management
- Reservation workflow functions
- Error handling and edge cases
"""

import unittest
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock, Mock
import requests

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import integration script functions
from integration.reservia_integration import (
    get_username,
    check_no_auth_mode,
    login,
    reserve_resource,
    check_reservation_status,
    send_keep_alive,
    send_release,
    cleanup_reservation,
    RESOURCE_ID
)


class TestIntegrationScript(unittest.TestCase):
    """Test cases for reservia integration script functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:5000"
        self.test_username = "testuser"
        
    @patch('subprocess.run')
    def test_get_username_success(self, mock_run):
        """Test successful username retrieval"""
        mock_result = Mock()
        mock_result.stdout = "testuser\n"
        mock_run.return_value = mock_result
        
        username = get_username()
        
        self.assertEqual(username, "testuser")
        mock_run.assert_called_once_with(['whoami'], capture_output=True, text=True, check=True)

    @patch('subprocess.run')
    @patch('sys.exit')
    def test_get_username_failure(self, mock_exit, mock_run):
        """Test username retrieval failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'whoami')
        
        get_username()
        
        mock_exit.assert_called_once_with(1)

    @patch('requests.get')
    def test_check_no_auth_mode_enabled(self, mock_get):
        """Test checking no-auth mode when enabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "alive", "no_auth": True}
        mock_get.return_value = mock_response
        
        result = check_no_auth_mode(self.base_url)
        
        self.assertTrue(result)
        mock_get.assert_called_once_with(f"{self.base_url}/info/is_alive")

    @patch('requests.get')
    def test_check_no_auth_mode_disabled(self, mock_get):
        """Test checking no-auth mode when disabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "alive", "no_auth": False}
        mock_get.return_value = mock_response
        
        result = check_no_auth_mode(self.base_url)
        
        self.assertFalse(result)

    @patch('requests.get')
    @patch('sys.exit')
    def test_check_no_auth_mode_server_error(self, mock_exit, mock_get):
        """Test checking no-auth mode with server error"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        check_no_auth_mode(self.base_url)
        
        mock_exit.assert_called_once_with(1)

    @patch('integration.reservia_integration.get_username')
    @patch('integration.reservia_integration.check_no_auth_mode')
    @patch('requests.Session')
    def test_login_no_auth_success(self, mock_session_class, mock_check_no_auth, mock_get_username):
        """Test successful login in no-auth mode"""
        # Setup mocks
        mock_get_username.return_value = self.test_username
        mock_check_no_auth.return_value = True
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        
        # Test login
        result = login(self.base_url)
        
        # Assertions
        self.assertEqual(result, mock_session)
        mock_session.post.assert_called_once_with(
            f"{self.base_url}/session/login", 
            json={"name": self.test_username}
        )

    @patch('integration.reservia_integration.get_username')
    @patch('integration.reservia_integration.check_no_auth_mode')
    @patch('requests.Session')
    def test_login_auth_required(self, mock_session_class, mock_check_no_auth, mock_get_username):
        """Test login when authentication is required"""
        mock_get_username.return_value = self.test_username
        mock_check_no_auth.return_value = False
        
        # Mock session to avoid creating actual session object
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Should raise SystemExit when auth is required
        with self.assertRaises(SystemExit) as cm:
            login(self.base_url)
        
        self.assertEqual(cm.exception.code, 1)

    def test_reserve_resource_success(self):
        """Test successful resource reservation"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        
        # Should not raise exception
        reserve_resource(mock_session, self.base_url)
        
        mock_session.post.assert_called_once_with(
            f"{self.base_url}/reservation/request",
            json={"resource_id": RESOURCE_ID}
        )

    @patch('sys.exit')
    def test_reserve_resource_failure(self, mock_exit):
        """Test resource reservation failure"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 409
        mock_session.post.return_value = mock_response
        
        reserve_resource(mock_session, self.base_url)
        
        mock_exit.assert_called_once_with(1)

    def test_check_reservation_status_approved(self):
        """Test checking reservation status - approved"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "reservation": {"status": "approved"}
        }
        mock_session.get.return_value = mock_response
        
        status = check_reservation_status(mock_session, self.base_url)
        
        self.assertEqual(status, "approved")

    def test_check_reservation_status_none(self):
        """Test checking reservation status - no reservation"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"reservation": None}
        mock_session.get.return_value = mock_response
        
        status = check_reservation_status(mock_session, self.base_url)
        
        self.assertIsNone(status)

    def test_send_keep_alive_success(self):
        """Test successful keep-alive message"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        
        # Should not raise exception
        send_keep_alive(mock_session, self.base_url)
        
        mock_session.post.assert_called_once_with(
            f"{self.base_url}/reservation/keep_alive",
            json={"resource_id": RESOURCE_ID}
        )

    def test_send_release_success(self):
        """Test successful resource release"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        
        # Should not raise exception
        send_release(mock_session, self.base_url)
        
        mock_session.post.assert_called_once_with(
            f"{self.base_url}/reservation/release",
            json={"resource_id": RESOURCE_ID}
        )

    @patch('integration.reservia_integration.check_reservation_status')
    def test_cleanup_reservation_requested(self, mock_check_status):
        """Test cleanup for requested reservation"""
        mock_check_status.return_value = "requested"
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        
        result = cleanup_reservation(mock_session, self.base_url)
        
        self.assertTrue(result)
        mock_session.post.assert_called_once_with(
            f"{self.base_url}/reservation/cancel",
            json={"resource_id": RESOURCE_ID}
        )

    @patch('integration.reservia_integration.check_reservation_status')
    def test_cleanup_reservation_approved(self, mock_check_status):
        """Test cleanup for approved reservation"""
        mock_check_status.return_value = "approved"
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        
        result = cleanup_reservation(mock_session, self.base_url)
        
        self.assertTrue(result)
        mock_session.post.assert_called_once_with(
            f"{self.base_url}/reservation/release",
            json={"resource_id": RESOURCE_ID}
        )

    @patch('integration.reservia_integration.check_reservation_status')
    def test_cleanup_reservation_unknown_status(self, mock_check_status):
        """Test cleanup for unknown reservation status"""
        mock_check_status.return_value = "unknown"
        
        mock_session = Mock()
        
        result = cleanup_reservation(mock_session, self.base_url)
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()