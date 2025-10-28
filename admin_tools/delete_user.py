#!/usr/bin/env python3

import os
import sys
sys.path.append('..')

from backend.app.database import Database, User, Password, ReservationLifecycle

if len(sys.argv) != 2:
    print("Usage: python3 delete_user.py <username>")
    sys.exit(1)

username = sys.argv[1]

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': '../data',
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    user = db.session.query(User).filter(User.name == username).first()
    if not user:
        print(f"Error: User '{username}' not found")
        sys.exit(1)
    
    # Check for active reservations
    active_reservations = db.session.query(ReservationLifecycle).filter(
        ReservationLifecycle.user_id == user.id,
        ReservationLifecycle.cancelled_date.is_(None),
        ReservationLifecycle.released_date.is_(None)
    ).count()
    
    if active_reservations > 0:
        print(f"Error: User '{username}' has {active_reservations} active reservations. Cancel them first.")
        sys.exit(1)
    
    # Delete password entry
    password_entry = db.session.query(Password).filter(Password.user_id == user.id).first()
    if password_entry:
        db.session.delete(password_entry)
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    print(f"Deleted user: {username}")