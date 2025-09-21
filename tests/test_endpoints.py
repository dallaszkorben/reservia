import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import Database
from backend.app.application import ReserviaApp

def cleanup_test_databases():
    """Clean up test database files and reset singleton"""
    HOME = str(Path.home())
    test_path = os.path.join(HOME, '.reservia_test_admin')
    
    if os.path.exists(test_path):
        import shutil
        shutil.rmtree(test_path)

    # Reset singleton
    Database._instance = None

def test_admin_user_add():
    cleanup_test_databases()
    
    config_dict = {
        'app_name': 'reservia_test_admin',
        'version': '1.0.0',
        'log': {'log_name': 'test.log', 'level': 'DEBUG', 'backupCount': 1},
        'database': {'name': 'test_admin.db'}
    }
    
    # Create test app
    reservia_app = ReserviaApp(config_dict)
    app = reservia_app.create_app()
    
    with app.test_client() as client:
        # Test admin user add endpoint
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'Test User', 'email': 'test@example.com'}),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert 'user_id' in data
        
        # Test missing fields
        response = client.post('/admin/user/add',
                             data=json.dumps({'name': 'Test User'}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    print("Admin user add tests passed!")

if __name__ == "__main__":
    test_admin_user_add()