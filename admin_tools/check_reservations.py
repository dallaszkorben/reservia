#!/usr/bin/env python3

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from backend.app.database import Database, ReservationLifecycle
from backend.app.utils import epoch_to_iso8601

config_dict = {
    'app_name': 'Reservia',
    'version': '1.0.0',
    'data_dir': os.path.join(project_root, 'data'),
    'log': {'log_name': 'reservia.log', 'level': 'INFO', 'backupCount': 5},
    'database': {'name': 'reservia.db'}
}

db = Database.get_instance(config_dict)

with db.lock:
    total_count = db.session.query(ReservationLifecycle).count()
    reservations = db.session.query(ReservationLifecycle).order_by(ReservationLifecycle.id.desc()).limit(10).all()
    
    print(f"Total reservations: {total_count} (showing latest 10)")
    print("-" * 80)
    
    for r in reservations:
        status = "CANCELLED" if r.cancelled_date else "RELEASED" if r.released_date else "APPROVED" if r.approved_date else "REQUESTED"
        request_time = epoch_to_iso8601(r.request_date)
        valid_until = epoch_to_iso8601(r.valid_until_date) if r.valid_until_date else "No expiration"
        
        print(f"ID: {r.id:2d} | User: {r.user.name:12s} | Resource: {r.resource.name:15s} | Status: {status:9s}")
        print(f"      Requested: {request_time} | Valid until: {valid_until}")
        print()