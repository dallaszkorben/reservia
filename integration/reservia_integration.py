#!/usr/bin/env python3
"""
Reservia Integration Script

This script demonstrates the complete workflow for interacting with the Reservia 
resource reservation system:

1. Login with user credentials
2. Reserve a resource (or check existing reservation)
3. Wait for approval if needed
4. Execute a mock script while maintaining the reservation
5. Release the resource when work is complete

The script handles the full lifecycle including keep-alive messages to prevent
reservation expiration and proper cleanup.

Author: Generated for Reservia integration testing
Requirements: requests library, Python 3.6+
"""

import requests
import time
import subprocess
import os
import sys
import hashlib

# =============================================================================
# CONFIGURATION
# =============================================================================

# Reservia server configuration
RESERVIA_BASE_URL = "https://reservia.bss.seli.gic.ericsson.se"
RESOURCE_ID = 1
USERNAME = "user1"
PASSWORD = "user1"

# Timing configuration (in seconds)
STATUS_CHECK_INTERVAL = 10    # How often to check reservation status while waiting
KEEP_ALIVE_INTERVAL = 10      # How often to send keep-alive while script runs

# =============================================================================
# AUTHENTICATION & SESSION MANAGEMENT
# =============================================================================

def login():
    """
    Authenticate with Reservia server and establish session.
    
    The Reservia API requires SHA-256 hashed passwords and uses session cookies
    for subsequent authentication. The requests.Session() automatically handles
    cookie management.
    
    Returns:
        requests.Session: Authenticated session object for API calls
        
    Exits:
        System exit on authentication failure
    """
    print(f"Logging in as {USERNAME}...")
    
    # Create session for cookie management
    session = requests.Session()
    
    # Hash password as required by Reservia API
    hashed_password = hashlib.sha256(PASSWORD.encode()).hexdigest()
    
    # Prepare login payload
    login_data = {
        "name": USERNAME, 
        "password": hashed_password
    }
    
    # Attempt login
    response = session.post(f"{RESERVIA_BASE_URL}/session/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed with status code: {response.status_code}")
        print("Check username/password and server availability")
        sys.exit(1)
    
    print("✅ Login successful")
    return session

# =============================================================================
# RESERVATION MANAGEMENT
# =============================================================================

def reserve_resource(session):
    """
    Request a new resource reservation.
    
    Args:
        session (requests.Session): Authenticated session
        
    Exits:
        System exit on reservation failure
    """
    print(f"Requesting reservation for resource {RESOURCE_ID}...")
    
    reserve_data = {"resource_id": RESOURCE_ID}
    response = session.post(f"{RESERVIA_BASE_URL}/reservation/request", json=reserve_data)
    
    # Accept both 200 (OK) and 201 (Created) as success
    if response.status_code not in [200, 201]:
        print(f"❌ Reservation failed with status code: {response.status_code}")
        if response.status_code == 409:
            print("Conflict: User may already have an active reservation")
        sys.exit(1)
    
    print(f"✅ Resource {RESOURCE_ID} reservation requested")

def check_reservation_status(session):
    """
    Check the current status of user's reservation for the target resource.
    
    Args:
        session (requests.Session): Authenticated session
        
    Returns:
        str or None: Reservation status ("requested", "approved") or None if no reservation
        
    Exits:
        System exit on API failure
    """
    response = session.get(f"{RESERVIA_BASE_URL}/reservation/active?resource_id={RESOURCE_ID}")
    
    if response.status_code != 200:
        print(f"❌ Status check failed with status code: {response.status_code}")
        sys.exit(1)
    
    # Parse response to find user's reservation
    reservations = response.json().get("reservations", [])
    
    # Search for this user's reservation for the target resource
    for reservation in reservations:
        if (reservation.get("resource_id") == RESOURCE_ID and 
            reservation.get("user_name") == USERNAME):
            return reservation.get("status")
    
    return None  # No reservation found

def send_keep_alive(session):
    """
    Send keep-alive message to extend reservation validity.
    
    Keep-alive messages prevent the reservation from expiring due to timeout.
    This is essential for maintaining approved reservations during long-running tasks.
    
    Args:
        session (requests.Session): Authenticated session
        
    Exits:
        System exit on API failure
    """
    keep_alive_data = {"resource_id": RESOURCE_ID}
    response = session.post(f"{RESERVIA_BASE_URL}/reservation/keep_alive", json=keep_alive_data)
    
    if response.status_code != 200:
        print(f"❌ Keep alive failed with status code: {response.status_code}")
        sys.exit(1)
    
    print("⏰ Keep alive sent")

def send_release(session):
    """
    Release the approved reservation, making the resource available to others.
    
    Args:
        session (requests.Session): Authenticated session
        
    Exits:
        System exit on API failure
    """
    print("Releasing resource...")
    
    release_data = {"resource_id": RESOURCE_ID}
    response = session.post(f"{RESERVIA_BASE_URL}/reservation/release", json=release_data)
    
    if response.status_code != 200:
        print(f"❌ Release failed with status code: {response.status_code}")
        sys.exit(1)
    
    print("✅ Resource released successfully")

# =============================================================================
# PROCESS MANAGEMENT
# =============================================================================

def is_process_running(process):
    """
    Check if a subprocess is still running.
    
    Args:
        process (subprocess.Popen): Process object to check
        
    Returns:
        bool: True if process is still running, False if completed
    """
    return process.poll() is None

def execute_mock_script():
    """
    Start the mock script as a subprocess.
    
    Returns:
        subprocess.Popen: Process object for monitoring
    """
    script_path = os.path.join(os.path.dirname(__file__), "mock_script.py")
    
    if not os.path.exists(script_path):
        print(f"❌ Mock script not found: {script_path}")
        sys.exit(1)
    
    print("🚀 Starting mock script...")
    process = subprocess.Popen([sys.executable, script_path])
    print(f"📋 Mock script started with PID: {process.pid}")
    
    return process

# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def wait_for_approval(session):
    """
    Wait for reservation approval, sending keep-alive messages as needed.
    
    Args:
        session (requests.Session): Authenticated session
    """
    print("⏳ Waiting for reservation approval...")
    
    while True:
        status = check_reservation_status(session)
        
        if status == "requested":
            print("📋 Status: Requested - sending keep-alive...")
            send_keep_alive(session)
            time.sleep(STATUS_CHECK_INTERVAL)
            
        elif status == "approved":
            print("✅ Reservation approved!")
            return
            
        elif status is None:
            print("❌ No reservation found")
            sys.exit(1)
            
        else:
            print(f"❌ Unknown reservation status: {status}")
            sys.exit(1)

def monitor_script_execution(session, process):
    """
    Monitor script execution while maintaining reservation with keep-alive messages.
    
    Args:
        session (requests.Session): Authenticated session
        process (subprocess.Popen): Running script process
    """
    print("🔄 Monitoring script execution...")
    
    while True:
        if is_process_running(process):
            # Script still running - send keep-alive to maintain reservation
            send_keep_alive(session)
            time.sleep(KEEP_ALIVE_INTERVAL)
        else:
            # Script completed
            print("✅ Mock script completed successfully")
            return

def main():
    """
    Main workflow orchestration.
    
    Implements the complete Reservia integration workflow:
    1. Authentication
    2. Reservation management
    3. Script execution with monitoring
    4. Resource cleanup
    """
    print("=" * 60)
    print("🎯 RESERVIA INTEGRATION SCRIPT")
    print("=" * 60)
    
    try:
        # Step 1: Authenticate with Reservia
        session = login()
        
        # Step 2: Check for existing reservation or create new one
        existing_status = check_reservation_status(session)
        
        if existing_status:
            print(f"📋 Found existing reservation with status: {existing_status}")
            if existing_status == "requested":
                wait_for_approval(session)
        else:
            # No existing reservation - create new one
            reserve_resource(session)
            wait_for_approval(session)
        
        # Step 3: Execute mock script with monitoring
        process = execute_mock_script()
        monitor_script_execution(session, process)
        
        # Step 4: Clean up - release the resource
        send_release(session)
        
        print("=" * 60)
        print("🎉 WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
