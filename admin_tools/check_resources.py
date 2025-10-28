#!/usr/bin/env python3

import os
import sys
sys.path.append('..')

from backend.app.database import Database, Resource

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': '../data',
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    resources = db.session.query(Resource).all()
    print(f"Total resources: {len(resources)}")
    print("-" * 60)
    for resource in resources:
        comment = resource.comment or "No comment"
        print(f"ID: {resource.id:2d} | Name: {resource.name:20s} | Comment: {comment}")