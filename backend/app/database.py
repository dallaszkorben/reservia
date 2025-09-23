import os
import logging
import hashlib
import threading
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .constants import LOG_PREFIX_DATABASE
from .utils import get_current_epoch, epoch_to_iso8601
from flask import session

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    comment = Column(String, nullable=True)

class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    password = Column(String, nullable=False)

    user = relationship("User")

class Request(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    request_date = Column(Integer, nullable=False)
    approved_date = Column(Integer, nullable=True)
    cancelled_date = Column(Integer, nullable=True)

    user = relationship("User")
    resource = relationship("Resource")

class Database:
    _instance = None

    def __init__(self, config_dict=None):
        if hasattr(self, '_initialized'):
            return

        self.config_dict = config_dict
        self.lock = threading.Lock()
        self._setup_database()
        self._initialized = True

    @staticmethod
    def get_instance(config_dict=None):
        if Database._instance is None:
            Database._instance = Database(config_dict)
        return Database._instance

    def _setup_database(self):
        HOME = str(Path.home())
        FOLDER = "." + self.config_dict['app_name']
        db_dir = os.path.join(HOME, FOLDER)
        os.makedirs(db_dir, exist_ok=True)

        db_path = os.path.join(db_dir, self.config_dict['database']['name'])
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self._create_default_admin()
        logging.info(f"{LOG_PREFIX_DATABASE}Database initialized at {db_path}")

    def _create_default_admin(self):
        with self.lock:
            existing_admin = self.session.query(User).filter(User.email == "admin@admin.se").first()
            if not existing_admin:
                admin_user = User(name="admin", email="admin@admin.se")
                self.session.add(admin_user)
                self.session.flush()

                encoded_password = hashlib.sha256("admin".encode()).hexdigest()
                password_entry = Password(user_id=admin_user.id, password=encoded_password)
                self.session.add(password_entry)
                self.session.commit()

                logging.info(f"{LOG_PREFIX_DATABASE}Default admin user created with password hash: {encoded_password[:10]}...")

    # === Session ===

    def login(self, name, password):
        with self.lock:
            user = self.session.query(User).filter(User.name == name).first()
            if not user:
                logging.error(f"{LOG_PREFIX_DATABASE}The given user '{name}' to login does not exist")
                return None

            password_entry = self.session.query(Password).filter(Password.user_id == user.id).first()
            if not password_entry:
                logging.error(f"{LOG_PREFIX_DATABASE}It should not happen. There was NO password found for the given name '{name} in the database'")
                return None

            encoded_password = hashlib.sha256(password.encode()).hexdigest()
            logging.debug(f"{LOG_PREFIX_DATABASE}Login attempt - stored: {password_entry.password[:10]}..., provided: {encoded_password[:10]}...")
            if password_entry.password != encoded_password:
                logging.error(f"{LOG_PREFIX_DATABASE}The given password for user '{name}' is incorrect")
                return None

            logging.info(f"{LOG_PREFIX_DATABASE}User '{name}' logged in successfully")

            session['logged_in_user'] = {
                'user_id': user.id,
                'user_email': user.email,
                'user_name': user.name
            }
            session.permanent = True

            return user

    def logout(self):
        if 'logged_in_user' in session:
            user_name = session['logged_in_user'].get('user_name', 'unknown')
            session.clear()
            session.permanent = False
            logging.info(f"{LOG_PREFIX_DATABASE}User '{user_name}' logged out successfully")
            return True
        return False

    def is_logged_in(self):
        return 'logged_in_user' in session

    def get_current_user(self):
        with self.lock:
            if not self.is_logged_in():
                logging.info(f"{LOG_PREFIX_DATABASE}No user is currently logged in")
                return None
            logging.info(f"{LOG_PREFIX_DATABASE}User is currently logged in")
            return session['logged_in_user']

    # === Users ===

    def create_user(self, name, email, password):
        # Only admin can create users
        current_user = self.get_current_user()
        if not current_user or current_user['user_name'] != 'admin':
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized user creation attempt")
            return None

        with self.lock:
            user = User(name=name, email=email)
            self.session.add(user)
            self.session.flush()

            encoded_password = hashlib.sha256(password.encode()).hexdigest()
            password_entry = Password(user_id=user.id, password=encoded_password)
            self.session.add(password_entry)
            self.session.commit()

            logging.info(f"{LOG_PREFIX_DATABASE}User created: {name} ({email})")
            return user

    def update_user(self, email=None, password=None):

        # Only logged-in users can update their own profile
        current_user = self.get_current_user()
        if not current_user:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized user update attempt")
            return None

        with self.lock:
            user_id = current_user['user_id']
            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            if email is not None:
                user.email = email
                # Update session with new email
                session['logged_in_user']['user_email'] = email

            if password is not None:
                encoded_password = hashlib.sha256(password.encode()).hexdigest()
                password_entry = self.session.query(Password).filter(Password.user_id == user_id).first()
                if password_entry:
                    password_entry.password = encoded_password

            self.session.commit()
            logging.info(f"{LOG_PREFIX_DATABASE}User updated: {user.name} (ID: {user_id})")
            return user

    def get_users(self):
        with self.lock:
            users = self.session.query(User).all()
            logging.info(f"{LOG_PREFIX_DATABASE}Retrieved {len(users)} users")
            return users

    # === Resource ===

    def create_resource(self, name, comment=None):
        # Only admin can create resources
        current_user = self.get_current_user()
        if not current_user or current_user['user_name'] != 'admin':
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized resource creation attempt")
            return None

        with self.lock:
            resource = Resource(name=name, comment=comment)
            self.session.add(resource)
            self.session.commit()
            logging.info(f"{LOG_PREFIX_DATABASE}Resource created: {name}")
            return resource

    def get_resources(self):
        with self.lock:
            resources = self.session.query(Resource).all()
            logging.info(f"{LOG_PREFIX_DATABASE}Retrieved {len(resources)} resources")
            return resources

    # === Request ===

    def create_request_for_resource(self, resource_id):
        # Only logged-in users can send requests
        current_user = self.get_current_user()
        if not current_user:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized request attempt - user not logged in")
            return None

        with self.lock:
            user_id = current_user['user_id']
            
            # Verify resource exists
            resource = self.session.query(Resource).filter(Resource.id == resource_id).first()
            if not resource:
                logging.error(f"{LOG_PREFIX_DATABASE}Resource with ID {resource_id} not found")
                return None

            # Create request
            request_epoch = get_current_epoch()
            request = Request(
                user_id=user_id,
                resource_id=resource_id,
                request_date=request_epoch
            )
            self.session.add(request)
            self.session.commit()

            request_iso = epoch_to_iso8601(request_epoch)
            user_name = current_user['user_name']
            resource_name = resource.name
            logging.info(f"{LOG_PREFIX_DATABASE}Request created: User {user_id} ({user_name}) requested Resource {resource_id} ({resource_name}) at {request_iso}")
            return request

    def update_request_for_resource(self, request_id, approved_date=None, cancelled_date=None):
        with self.lock:
            # Find the request
            request = self.session.query(Request).filter(Request.id == request_id).first()
            if not request:
                logging.error(f"{LOG_PREFIX_DATABASE}Request with ID {request_id} not found")
                return None

            # Update fields if provided
            if approved_date is not None:
                request.approved_date = approved_date
            
            if cancelled_date is not None:
                request.cancelled_date = cancelled_date

            self.session.commit()
            
            # Get user and resource names for logging
            user = request.user
            resource = request.resource
            request_date_iso = epoch_to_iso8601(request.request_date)
            
            # Build log message with detailed information
            log_msg = f"Request {request_id} updated: User {user.id} ({user.name}) for Resource {resource.id} ({resource.name}), requested at {request_date_iso}"
            
            if approved_date is not None:
                approved_iso = epoch_to_iso8601(approved_date)
                log_msg += f", approved at {approved_iso}"
            
            if cancelled_date is not None:
                cancelled_iso = epoch_to_iso8601(cancelled_date)
                log_msg += f", cancelled at {cancelled_iso}"
            
            logging.info(f"{LOG_PREFIX_DATABASE}{log_msg}")
            return request

