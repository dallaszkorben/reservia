import os
import logging
import logging.handlers
import hashlib
from pathlib import Path
from flask import Flask
from .views.info_bp import InfoBlueprintManager
from .views.home_bp import HomeBlueprintManager
from .views.admin_bp import AdminBlueprintManager
from .views.session_bp import SessionBlueprintManager
from .views.reservation_bp import ReservationBlueprintManager
from .database import Database
from datetime import datetime, timedelta

class ReserviaApp(Flask):
    """Main application class for Reservia"""

    def __init__(self, config_dict=None):

        super().__init__(config_dict['app_name'])

        self.app = self
        self.config_dict = config_dict

        salt = "my very secret key"
        self.secret_key = hashlib.sha256(salt.encode()).hexdigest()
        self.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
        self.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for development

        self._configure_logging()

        self.database = Database.get_instance(self.config_dict)

        # Store application config in Flask's config for global access
        # This allows accessing config_dict from anywhere in the app via current_app.config['APP_CONFIG']
        # For example:
        # from flask import current_app
        # print(current_app.config['APP_CONFIG'])
        self.app.config['APP_CONFIG'] = self.config_dict

        self._register_blueprints()

        return None

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
        admin_manager = AdminBlueprintManager()
        session_manager = SessionBlueprintManager()
        reservation_manager = ReservationBlueprintManager()

        self.app.register_blueprint(home_manager.get_blueprint())
        self.app.register_blueprint(info_manager.get_blueprint())
        self.app.register_blueprint(admin_manager.get_blueprint())
        self.app.register_blueprint(session_manager.get_blueprint())
        self.app.register_blueprint(reservation_manager.get_blueprint())