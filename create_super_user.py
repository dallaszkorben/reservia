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
    existing_super = db.session.query(User).filter(User.email == "super@super.se").first()
    if not existing_super:
        super_user = User(name="super", email="super@super.se", role="super")
        db.session.add(super_user)
        db.session.flush()
        
        encoded_password = hashlib.sha256("super".encode()).hexdigest()
        password_entry = Password(user_id=super_user.id, password=encoded_password)
        db.session.add(password_entry)
        db.session.commit()
        
        print(f"Created super user with password hash: {encoded_password[:10]}...")
    else:
        print("Super user already exists")