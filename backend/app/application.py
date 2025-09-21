import os
import logging
import logging.handlers
from pathlib import Path
from flask import Flask
from .views.info_bp import InfoBlueprintManager
from .views.home_bp import HomeBlueprintManager
from .database import Database

class ReserviaApp:
    """Main application class for Reservia"""

    def __init__(self, config_dict=None):
        self.app = None
        self.config_dict = config_dict

    def create_app(self):
        """Factory method to create Flask application"""
        self._configure_logging()

        self.database = Database.get_instance(self.config_dict)

        self.app = Flask(__name__,
                        template_folder='../../frontend/templates',
                        static_folder='../../frontend/static')

        self.app.config['APP_CONFIG'] = self.config_dict

        self._register_blueprints()
        return self.app

    def _configure_logging(self):
        """Configure application logging"""
        HOME = str(Path.home())
        FOLDER = "." + self.config_dict['app_name']
        log_dir = os.path.join(HOME, FOLDER)

        os.makedirs(log_dir, exist_ok=True)

        log_file_path = os.path.join(log_dir, self.config_dict['log']['log_name'])
        log_level = getattr(logging, self.config_dict['log']['level'])
        backup_count = self.config_dict['log']['backupCount']

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.handlers.RotatingFileHandler(
                    log_file_path,
                    maxBytes=10*1024*1024,
                    backupCount=backup_count
                ),
                logging.StreamHandler()
            ]
        )

    def _register_blueprints(self):
        """Register all application blueprints"""
        home_manager = HomeBlueprintManager()
        info_manager = InfoBlueprintManager()

        self.app.register_blueprint(home_manager.get_blueprint())
        self.app.register_blueprint(info_manager.get_blueprint())