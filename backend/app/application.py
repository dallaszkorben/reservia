import os
import logging
import logging.handlers
import hashlib
import threading
import time
from pathlib import Path
from flask import Flask
from .views.info_bp import InfoBlueprintManager
from .views.home_bp import HomeBlueprintManager
from .views.admin_bp import AdminBlueprintManager
from .views.session_bp import SessionBlueprintManager
from .views.reservation_bp import ReservationBlueprintManager
from .database import Database
from datetime import datetime, timedelta
from ..config.config import CONFIG

class ReserviaApp(Flask):
    """Main application class for Reservia"""

    def __init__(self, config_dict=None):

        # Get absolute paths to templates and static folders
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        template_folder = os.path.join(project_root, 'frontend', 'templates')
        static_folder = os.path.join(project_root, 'frontend', 'static')
        
        super().__init__(config_dict['app_name'], template_folder=template_folder, static_folder=static_folder)

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

        # Expiration thread management
        self.expiration_thread = None
        self.stop_expiration_thread = False

        self._register_blueprints()
        self._start_expiration_thread()

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

    def _start_expiration_thread(self):
        """Start the background thread that checks for expired reservations."""
        if self.expiration_thread is None or not self.expiration_thread.is_alive():
            self.stop_expiration_thread = False
            self.expiration_thread = threading.Thread(target=self._expiration_worker, daemon=True)
            self.expiration_thread.start()
            logging.info("ReserviaApp: Expiration thread started")

    def _stop_expiration_thread(self):
        """Stop the background expiration thread."""
        self.stop_expiration_thread = True
        if self.expiration_thread and self.expiration_thread.is_alive():
            self.expiration_thread.join(timeout=2)
            logging.info("ReserviaApp: Expiration thread stopped")

    def _expiration_worker(self):
        """Background worker that checks for expired approved reservations."""
        interval = CONFIG['expiration_check_interval_sec']
        logging.info(f"ReserviaApp: Expiration worker started with {interval}s interval")
        
        while not self.stop_expiration_thread:
            try:
                self.database.check_expired_reservations()
            except Exception as e:
                logging.error(f"ReserviaApp: Error in expiration worker: {str(e)}")
            
            time.sleep(interval)
        
        logging.info("ReserviaApp: Expiration worker stopped")

    def shutdown(self):
        """Shutdown the application and clean up resources."""
        self._stop_expiration_thread()