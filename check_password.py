#!/usr/bin/env python3

import os
import sys
import hashlib
sys.path.append('.')

from backend.app.database import Database, User, Password

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': './data',
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    super_user = db.session.query(User).filter(User.name == "super").first()
    if super_user:
        password_entry = db.session.query(Password).filter(Password.user_id == super_user.id).first()
        if password_entry:
            print(f"Stored hash: {password_entry.password}")
            expected_hash = hashlib.sha256("super".encode()).hexdigest()
            print(f"Expected hash: {expected_hash}")
            print(f"Match: {password_entry.password == expected_hash}")
        else:
            print("No password entry found")
    else:
        print("Super user not found")