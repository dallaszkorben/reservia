#!/usr/bin/env python3

import os
import sys
import hashlib
sys.path.append('..')

from backend.app.database import Database, User, Password

if len(sys.argv) != 5:
    print("Usage: python3 create_user.py <name> <email> <password> <role>")
    print("Roles: user, admin, super")
    sys.exit(1)

name, email, password, role = sys.argv[1:5]

if role not in ['user', 'admin', 'super']:
    print("Error: Role must be 'user', 'admin', or 'super'")
    sys.exit(1)

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': '../data',
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    existing_user = db.session.query(User).filter(User.name == name).first()
    if existing_user:
        print(f"Error: User '{name}' already exists")
        sys.exit(1)
    
    existing_email = db.session.query(User).filter(User.email == email).first()
    if existing_email:
        print(f"Error: Email '{email}' already exists")
        sys.exit(1)
    
    user = User(name=name, email=email, role=role)
    db.session.add(user)
    db.session.flush()
    
    encoded_password = hashlib.sha256(password.encode()).hexdigest()
    password_entry = Password(user_id=user.id, password=encoded_password)
    db.session.add(password_entry)
    db.session.commit()
    
    print(f"Created user: {name} ({email}) with role '{role}'")