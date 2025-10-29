from backend.app.application import ReserviaApp
from backend.config.config import CONFIG
import os

# Add version to config
config_dict = CONFIG.copy()
config_dict['version'] = '1.0.0'

# Create application instance - Apache will use this 'app' variable
reservia_app = ReserviaApp(config_dict)


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    reservia_app.run(host='0.0.0.0', port=5000, debug=debug_mode)
