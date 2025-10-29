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
import argparse

# =============================================================================
# CONFIGURATION
# =============================================================================

# Reservia server configuration
RESERVIA_BASE_URL = "https://reservia.bss.seli.gic.ericsson.se"
RESOURCE_ID = 1
USERNAME = "user1"
PASSWORD = "user1"

# Default values
DEFAULT_SCRIPT = "mock_script.py"
DEFAULT_INTERVAL = 10  # seconds

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Reservia Integration Script - Reserve resource and execute script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 reservia_integration.py                           # Use defaults
  python3 reservia_integration.py --script my_script.py     # Python script
  python3 reservia_integration.py --script xcalc            # System command
  python3 reservia_integration.py --script /path/to/script  # Absolute path
  python3 reservia_integration.py --script ./work.sh        # Relative path
  python3 reservia_integration.py --script "sleep 30"       # Shell command
  python3 reservia_integration.py --interval 5              # 5-second intervals
        """
    )
    
    parser.add_argument(
        "--script", "-s",
        default=DEFAULT_SCRIPT,
        help=f"Script/command to execute (default: {DEFAULT_SCRIPT})"
    )
    
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Keep-alive interval in seconds (default: {DEFAULT_INTERVAL})"
    )
    
    return parser.parse_args()

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

def cleanup_reservation(session):
    """
    Clean up reservation based on its current status.
    Uses cancel for requested reservations, release for approved ones.
    
    Args:
        session (requests.Session): Authenticated session
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check current reservation status
    status = check_reservation_status(session)
    
    if status == "requested":
        print("Cancelling requested reservation...")
        cancel_data = {"resource_id": RESOURCE_ID}
        response = session.post(f"{RESERVIA_BASE_URL}/reservation/cancel", json=cancel_data)
        
        if response.status_code != 200:
            print(f"❌ Cancel failed with status code: {response.status_code}")
            return False
        
        print("✅ Reservation cancelled successfully")
        return True
        
    elif status == "approved":
        print("Releasing approved reservation...")
        release_data = {"resource_id": RESOURCE_ID}
        response = session.post(f"{RESERVIA_BASE_URL}/reservation/release", json=release_data)
        
        if response.status_code != 200:
            print(f"❌ Release failed with status code: {response.status_code}")
            return False
        
        print("✅ Reservation released successfully")
        return True
        
    else:
        print(f"❌ Cannot cleanup reservation with status: {status}")
        return False

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

def execute_mock_script(script_name):
    """
    Start the specified script/command as a subprocess.
    
    Args:
        script_name (str): Path to script/executable or command name
    
    Returns:
        subprocess.Popen or None: Process object for monitoring, or None if failed
    """
    try:
        print(f"🚀 Starting: {script_name}")
        
        # Handle different types of executables
        if script_name.endswith('.py'):
            # Python script - use python interpreter
            if os.path.isabs(script_name) or '/' in script_name:
                # Absolute or relative path provided
                script_path = script_name
            else:
                # Just filename - look in current directory
                script_path = os.path.join(os.path.dirname(__file__), script_name)
            
            if not os.path.exists(script_path):
                print(f"❌ Python script not found: {script_path}")
                return None
                
            process = subprocess.Popen([sys.executable, script_path])
        else:
            # System command or executable
            process = subprocess.Popen(script_name, shell=True)
        
        print(f"📋 Process started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start '{script_name}': {e}")
        return None

# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def wait_for_approval(session, interval):
    """
    Wait for reservation approval, sending keep-alive messages as needed.
    
    Args:
        session (requests.Session): Authenticated session
        interval (int): Check interval in seconds
    """
    print("⏳ Waiting for reservation approval...")
    
    while True:
        status = check_reservation_status(session)
        
        if status == "requested":
            print("📋 Status: Requested - sending keep-alive...")
            send_keep_alive(session)
            time.sleep(interval)
            
        elif status == "approved":
            print("✅ Reservation approved!")
            return
            
        elif status is None:
            print("❌ No reservation found")
            sys.exit(1)
            
        else:
            print(f"❌ Unknown reservation status: {status}")
            sys.exit(1)

def monitor_script_execution(session, process, interval):
    """
    Monitor script execution while maintaining reservation with keep-alive messages.
    
    Args:
        session (requests.Session): Authenticated session
        process (subprocess.Popen): Running script process
        interval (int): Keep-alive interval in seconds
    """
    print("🔄 Monitoring script execution...")
    
    while True:
        if is_process_running(process):
            # Script still running - send keep-alive to maintain reservation
            send_keep_alive(session)
            time.sleep(interval)
        else:
            # Script completed
            print("✅ Script completed successfully")
            return

def main():
    """
    Main workflow orchestration.
    
    Implements the complete Reservia integration workflow:
    1. Parse command-line arguments
    2. Authentication
    3. Reservation management
    4. Script execution with monitoring
    5. Resource cleanup
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    print("=" * 60)
    print("🎯 RESERVIA INTEGRATION SCRIPT")
    print("=" * 60)
    print(f"📄 Script to execute: {args.script}")
    print(f"⏱️  Keep-alive interval: {args.interval} seconds")
    print("=" * 60)
    
    try:
        # Step 1: Authenticate with Reservia
        session = login()
        
        # Step 2: Check for existing reservation or create new one
        existing_status = check_reservation_status(session)
        
        if existing_status:
            print(f"📋 Found existing reservation with status: {existing_status}")
            if existing_status == "requested":
                wait_for_approval(session, args.interval)
        else:
            # No existing reservation - create new one
            reserve_resource(session)
            wait_for_approval(session, args.interval)
        
        # Step 3: Execute script with monitoring
        process = execute_mock_script(args.script)
        
        if process is None:
            # Script execution failed - cleanup the reservation
            print("⚠️  Script execution failed, cleaning up reservation...")
            cleanup_reservation(session)
            sys.exit(1)
        
        monitor_script_execution(session, process, args.interval)
        
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
