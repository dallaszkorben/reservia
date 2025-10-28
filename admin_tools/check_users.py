#!/usr/bin/env python3

import os
import sys
sys.path.append('..')

from backend.app.database import Database, User

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': '../data',
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    users = db.session.query(User).all()
    print(f"Total users: {len(users)}")
    print("-" * 50)
    for user in users:
        print(f"ID: {user.id:2d} | Name: {user.name:12s} | Email: {user.email:20s} | Role: {user.role}")