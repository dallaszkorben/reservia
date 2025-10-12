"""
Backend configuration settings for Reservia application.
"""

CONFIG = {
    'approved_keep_alive_sec': 600,     # Default 10 minutes (600 seconds)
    'requested_keep_alive_sec': 1800,   # Default 30 minutes (1800 seconds), If it is None or 0, not keep alive used for the 'not yet approved' reservations
    'app_name': 'reservia',
    'expiration_check_interval_sec': 1, # Check for expired reservations every 1 second
}