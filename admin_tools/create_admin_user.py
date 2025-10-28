#!/usr/bin/env python3

import os
import sys
import hashlib
sys.path.append('..')

from backend.app.database import Database, User, Password

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': '../data',
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    existing_admin = db.session.query(User).filter(User.name == "admin").first()
    if not existing_admin:
        admin_user = User(name="admin", email="admin@admin.se", role="admin")
        db.session.add(admin_user)
        db.session.flush()
        
        encoded_password = hashlib.sha256("admin".encode()).hexdigest()
        password_entry = Password(user_id=admin_user.id, password=encoded_password)
        db.session.add(password_entry)
        db.session.commit()
        
        print(f"Created admin user with password hash: {encoded_password[:10]}...")
    else:
        print("Admin user already exists")