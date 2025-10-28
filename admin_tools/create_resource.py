#!/usr/bin/env python3

import os
import sys
sys.path.append('..')

from backend.app.database import Database, Resource

if len(sys.argv) < 2:
    print("Usage: python3 create_resource.py <name> [comment]")
    sys.exit(1)

name = sys.argv[1]
comment = sys.argv[2] if len(sys.argv) > 2 else None

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': '../data',
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    existing_resource = db.session.query(Resource).filter(Resource.name == name).first()
    if existing_resource:
        print(f"Error: Resource '{name}' already exists")
        sys.exit(1)
    
    resource = Resource(name=name, comment=comment)
    db.session.add(resource)
    db.session.commit()
    
    print(f"Created resource: {name}" + (f" ({comment})" if comment else ""))