import os
import logging
import hashlib
import threading
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
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
    name = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

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

class ReservationLifecycle(Base):
    __tablename__ = 'reservation_lifecycle'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    request_date = Column(Integer, nullable=False)
    approved_date = Column(Integer, nullable=True)
    cancelled_date = Column(Integer, nullable=True)
    released_date = Column(Integer, nullable=True)

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
                admin_user = User(name="admin", email="admin@admin.se", is_admin=True)
                self.session.add(admin_user)
                self.session.flush()

                # Pre-hashed password for "admin" (client-side hashed)
                encoded_password = hashlib.sha256("admin".encode()).hexdigest()
                password_entry = Password(user_id=admin_user.id, password=encoded_password)
                self.session.add(password_entry)
                self.session.commit()

                logging.info(f"{LOG_PREFIX_DATABASE}Default admin user created with password hash: {encoded_password[:10]}...")

    # === Session ===

    def login(self, name, password):
        """
        Authenticate user and create session.

        Args:
            name (str): Username for authentication. Required.
            password (str): User password already hashed on client-side. Required.

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if login succeeded, False otherwise
                - data (User|None): User object on success, None on failure
                - error_code (str|None): Error code on failure (USER_NOT_FOUND, INVALID_PASSWORD), None on success
                - error_message (str|None): Human-readable error message on failure, None on success

        Example:
            success, user, error_code, error_msg = db.login("admin", "hashed_password")
            if success:
                print(f"Logged in as {user.name}")
            else:
                print(f"Login failed: {error_msg}")
        """
        with self.lock:
            user = self.session.query(User).filter(User.name == name).first()
            if not user:
                logging.error(f"{LOG_PREFIX_DATABASE}The given user '{name}' to login does not exist")
                return False, None, "USER_NOT_FOUND", f"User '{name}' does not exist"

            password_entry = self.session.query(Password).filter(Password.user_id == user.id).first()
            if not password_entry:
                logging.error(f"{LOG_PREFIX_DATABASE}It should not happen. There was NO password found for the given name '{name} in the database'")
                return False, None, "PASSWORD_NOT_FOUND", "Password entry not found"

            # Password is already hashed on client-side, compare directly
            logging.debug(f"{LOG_PREFIX_DATABASE}Login attempt - stored: {password_entry.password[:10]}..., provided: {password[:10]}...")
            if password_entry.password != password:
                logging.error(f"{LOG_PREFIX_DATABASE}The given password for user '{name}' is incorrect")
                return False, None, "INVALID_PASSWORD", "Invalid credentials"

            logging.info(f"{LOG_PREFIX_DATABASE}User '{name}' logged in successfully")

            session['logged_in_user'] = {
                'user_id': user.id,
                'user_email': user.email,
                'user_name': user.name,
                'is_admin': bool(user.is_admin)
            }
            session.permanent = True

            return True, user, None, None

    def logout(self):
        if 'logged_in_user' in session:
            user_name = session['logged_in_user'].get('user_name', 'unknown')
            session.clear()
            session.permanent = False
            logging.info(f"{LOG_PREFIX_DATABASE}User '{user_name}' logged out successfully")
            return True, None, None, None
        return False, None, "NO_SESSION", "No active session to logout"

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
        """
        Create a new user account (admin only).

        Args:
            name (str): Username for the new account. Required.
            email (str): Email address for the new account. Required.
            password (str): Password already hashed on client-side. Required.

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if user created, False otherwise
                - data (User|None): User object on success, None on failure
                - error_code (str|None): Error code on failure (UNAUTHORIZED), None on success
                - error_message (str|None): Human-readable error message on failure, None on success

        Example:
            success, user, error_code, error_msg = db.create_user("john", "john@example.com", "hashed_pass")
            if success:
                print(f"Created user {user.name} with ID {user.id}")
            else:
                print(f"User creation failed: {error_msg}")
        """
        # Only admin can create users
        current_user = self.get_current_user()
        if not current_user or not current_user.get('is_admin', False):
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized user creation attempt")
            return False, None, "UNAUTHORIZED", "Admin access required"

        with self.lock:
            try:
                user = User(name=name, email=email)
                self.session.add(user)
                self.session.flush()

                # Password is already hashed on client-side
                password_entry = Password(user_id=user.id, password=password)
                self.session.add(password_entry)
                self.session.commit()

                logging.info(f"{LOG_PREFIX_DATABASE}User created: {name} ({email})")
                return True, user, None, None
            except Exception as e:
                self.session.rollback()
                if "UNIQUE constraint failed: users.email" in str(e):
                    logging.error(f"{LOG_PREFIX_DATABASE}Email '{email}' already exists")
                    return False, None, "EMAIL_EXISTS", f"Email '{email}' already exists"
                elif "UNIQUE constraint failed: users.name" in str(e):
                    logging.error(f"{LOG_PREFIX_DATABASE}Username '{name}' already exists")
                    return False, None, "USERNAME_EXISTS", f"Username '{name}' already exists"
                else:
                    logging.error(f"{LOG_PREFIX_DATABASE}Error creating user: {str(e)}")
                    return False, None, "DATABASE_ERROR", "Database error occurred"


    def modify_user(self, user_id, email=None, password=None):
        """
        Modify user data (admin can modify any user, user can modify self).

        Args:
            user_id (int): ID of the user to modify. Required.
            email (str, optional): New email address. Defaults to None.
            password (str, optional): New password in plain text. Defaults to None.

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if user modified, False otherwise
                - data (User|None): User object on success, None on failure
                - error_code (str|None): Error code on failure, None on success
                - error_message (str|None): Human-readable error message on failure, None on success
        """
        current_user = self.get_current_user()
        if not current_user:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized user modification - user not logged in")
            return False, None, "UNAUTHORIZED", "User authentication required"

        # Admin can modify any user, regular user can only modify self
        if not current_user.get('is_admin', False) and current_user['user_id'] != user_id:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized user modification - user {current_user['user_id']} cannot modify user {user_id}")
            return False, None, "UNAUTHORIZED", "Cannot modify other users"

        with self.lock:
            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                logging.error(f"{LOG_PREFIX_DATABASE}User with ID {user_id} not found")
                return False, None, "USER_NOT_FOUND", f"User {user_id} not found"

            try:
                if email is not None:
                    user.email = email
                    # Update session if modifying current user
                    if current_user['user_id'] == user_id:
                        session['logged_in_user']['user_email'] = email

                if password is not None:
                    # Password is already hashed on client-side
                    password_entry = self.session.query(Password).filter(Password.user_id == user_id).first()
                    if password_entry:
                        password_entry.password = password

                self.session.commit()
                logging.info(f"{LOG_PREFIX_DATABASE}User modified: {user.name} (ID: {user_id})")
                return True, user, None, None
            except Exception as e:
                self.session.rollback()
                if "UNIQUE constraint failed: users.email" in str(e):
                    logging.error(f"{LOG_PREFIX_DATABASE}Email '{email}' already exists")
                    return False, None, "EMAIL_EXISTS", f"Email '{email}' already exists"
                else:
                    logging.error(f"{LOG_PREFIX_DATABASE}Error modifying user: {str(e)}")
                    return False, None, "DATABASE_ERROR", "Database error occurred"

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
                # Password is already hashed on client-side
                password_entry = self.session.query(Password).filter(Password.user_id == user_id).first()
                if password_entry:
                    password_entry.password = password

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
        """
        Create a new resource for reservation (admin only).

        Args:
            name (str): Name of the resource. Required.
            comment (str, optional): Description or comment about the resource. Defaults to None.

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if resource created, False otherwise
                - data (Resource|None): Resource object on success, None on failure
                - error_code (str|None): Error code on failure (UNAUTHORIZED), None on success
                - error_message (str|None): Human-readable error message on failure, None on success

        Example:
            success, resource, error_code, error_msg = db.create_resource("Meeting Room A", "10 person capacity")
            if success:
                print(f"Created resource {resource.name} with ID {resource.id}")
            else:
                print(f"Resource creation failed: {error_msg}")
        """
        # Only admin can create resources
        current_user = self.get_current_user()
        if not current_user or not current_user.get('is_admin', False):
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized resource creation attempt")
            return False, None, "UNAUTHORIZED", "Admin access required"

        with self.lock:
            try:
                resource = Resource(name=name, comment=comment)
                self.session.add(resource)
                self.session.commit()
                logging.info(f"{LOG_PREFIX_DATABASE}Resource created: {name}")
                return True, resource, None, None
            except Exception as e:
                self.session.rollback()
                if "UNIQUE constraint failed: resources.name" in str(e):
                    logging.error(f"{LOG_PREFIX_DATABASE}Resource name '{name}' already exists")
                    return False, None, "RESOURCE_EXISTS", f"Resource name '{name}' already exists"
                else:
                    logging.error(f"{LOG_PREFIX_DATABASE}Error creating resource: {str(e)}")
                    return False, None, "DATABASE_ERROR", "Database error occurred"

    def get_resources(self):
        """
        Retrieve all resources in the system (requires login).

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if resources retrieved, False otherwise
                - data (list|None): List of Resource objects on success, None on failure
                - error_code (str|None): Error code on failure (UNAUTHORIZED), None on success
                - error_message (str|None): Human-readable error message on failure, None on success

        Example:
            success, resources, error_code, error_msg = db.get_resources()
            if success:
                print(f"Retrieved {len(resources)} resources")
            else:
                print(f"Failed to retrieve resources: {error_msg}")
        """
        current_user = self.get_current_user()
        if not current_user:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized resource retrieval - user not logged in")
            return False, None, "UNAUTHORIZED", "User authentication required"

        with self.lock:
            resources = self.session.query(Resource).all()
            logging.info(f"{LOG_PREFIX_DATABASE}Retrieved {len(resources)} resources")
            return True, resources, None, None

    # === Request ===

    def request_reservation(self, resource_id):
        """
        Request a reservation for a resource. Auto-approves if resource is free, otherwise queues the request.

        Args:
            resource_id (int): ID of the resource to reserve. Required.

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if reservation created, False otherwise
                - data (ReservationLifecycle|None): Reservation object on success, None on failure
                - error_code (str|None): Error code on failure (AUTH_REQUIRED, RESOURCE_NOT_FOUND, DUPLICATE_RESERVATION), None on success
                - error_message (str|None): Human-readable error message on failure, None on success

        Example:
            success, reservation, error_code, error_msg = db.request_reservation(1)
            if success:
                status = "approved" if reservation.approved_date else "queued"
                print(f"Reservation {status} with ID {reservation.id}")
            else:
                print(f"Reservation failed: {error_msg}")
        """
        # Only logged-in users can request reservations
        current_user = self.get_current_user()
        if not current_user:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized approve reservation request - user not logged in")
            return False, None, "AUTH_REQUIRED", "User authentication required"

        with self.lock:
            user_id = current_user['user_id']

            # Verify resource exists
            resource = self.session.query(Resource).filter(Resource.id == resource_id).first()
            if not resource:
                logging.error(f"{LOG_PREFIX_DATABASE}Resource with ID {resource_id} not found")
                return False, None, "RESOURCE_NOT_FOUND", f"Resource {resource_id} not found"

            # Check if user already has reservation on this resource
            existing_reservation = self.session.query(ReservationLifecycle).filter(
                ReservationLifecycle.user_id == user_id,
                ReservationLifecycle.resource_id == resource_id,
                ReservationLifecycle.cancelled_date.is_(None),
                ReservationLifecycle.released_date.is_(None)
            ).first()

            if existing_reservation:
                logging.error(f"{LOG_PREFIX_DATABASE}User {user_id} already has reservation on Resource {resource_id}")
                return False, None, "DUPLICATE_RESERVATION", "User already has active reservation for this resource"

            # Create new reservation lifecycle record
            request_epoch = get_current_epoch()
            reservation = ReservationLifecycle(
                user_id=user_id,
                resource_id=resource_id,
                request_date=request_epoch
            )

            # Check if resource is free
            last_record = self.session.query(ReservationLifecycle).filter(
                ReservationLifecycle.resource_id == resource_id,
                ReservationLifecycle.cancelled_date.is_(None)
            ).order_by(ReservationLifecycle.request_date.desc()).first()

            is_free = True
            if last_record:
                # Resource is free only if last record is released
                if last_record.released_date is None:
                    is_free = False

            # If resource is free, auto-approve the reservation
            if is_free:
                reservation.approved_date = request_epoch

            self.session.add(reservation)
            self.session.commit()

            # Logging
            request_iso = epoch_to_iso8601(request_epoch)
            user_name = current_user['user_name']
            resource_name = resource.name
            status = "approved" if is_free else "requested"
            logging.info(f"{LOG_PREFIX_DATABASE}Reservation {status}: User {user_id} ({user_name}) for Resource {resource_id} ({resource_name}) at {request_iso}")

            return True, reservation, None, None

    def cancel_reservation(self, resource_id):
        """
        Cancel a queued (not yet approved) reservation for a resource.

        Args:
            resource_id (int): ID of the resource reservation to cancel. Required.

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if reservation cancelled, False otherwise
                - data (ReservationLifecycle|None): Cancelled reservation object on success, None on failure
                - error_code (str|None): Error code on failure (AUTH_REQUIRED, RESERVATION_NOT_FOUND), None on success
                - error_message (str|None): Human-readable error message on failure, None on success

        Example:
            success, reservation, error_code, error_msg = db.cancel_reservation(1)
            if success:
                print(f"Cancelled reservation ID {reservation.id}")
            else:
                print(f"Cancellation failed: {error_msg}")
        """
        # Only logged-in users can cancel reservations
        current_user = self.get_current_user()
        if not current_user:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized reservation cancellation - user not logged in")
            return False, None, "AUTH_REQUIRED", "User authentication required"

        with self.lock:
            user_id = current_user['user_id']

            # Find the reservation to cancel
            reservation = self.session.query(ReservationLifecycle).filter(
                ReservationLifecycle.user_id == user_id,
                ReservationLifecycle.resource_id == resource_id,
                ReservationLifecycle.request_date.isnot(None),
                ReservationLifecycle.approved_date.is_(None),
                ReservationLifecycle.cancelled_date.is_(None),
                ReservationLifecycle.released_date.is_(None)
            ).first()

            if not reservation:
                logging.error(f"{LOG_PREFIX_DATABASE}No active reservation found for User {user_id} on Resource {resource_id}")
                return False, None, "RESERVATION_NOT_FOUND", "No queued reservation found to cancel"

            # Cancel the reservation
            cancel_epoch = get_current_epoch()
            reservation.cancelled_date = cancel_epoch
            self.session.commit()

            # Logging
            cancel_iso = epoch_to_iso8601(cancel_epoch)
            user_name = current_user['user_name']
            resource_name = reservation.resource.name
            logging.info(f"{LOG_PREFIX_DATABASE}Reservation cancelled: User {user_id} ({user_name}) for Resource {resource_id} ({resource_name}) at {cancel_iso}")

            return True, reservation, None, None

    def release_reservation(self, resource_id):
        """
        Release an approved reservation, freeing the resource. Auto-approves next queued user if any.

        Args:
            resource_id (int): ID of the resource reservation to release. Required.

        Returns:
            tuple: (success, data, error_code, error_message)
                - success (bool): True if reservation released, False otherwise
                - data (ReservationLifecycle|None): Released reservation object on success, None on failure
                - error_code (str|None): Error code on failure (AUTH_REQUIRED, RESERVATION_NOT_FOUND), None on success
                - error_message (str|None): Human-readable error message on failure, None on success

        Example:
            success, reservation, error_code, error_msg = db.release_reservation(1)
            if success:
                print(f"Released reservation ID {reservation.id}")
            else:
                print(f"Release failed: {error_msg}")
        """
        # Only logged-in users can release reservations
        current_user = self.get_current_user()
        if not current_user:
            logging.error(f"{LOG_PREFIX_DATABASE}Unauthorized reservation release - user not logged in")
            return False, None, "AUTH_REQUIRED", "User authentication required"

        with self.lock:
            user_id = current_user['user_id']

            # Find the reservation to release
            reservation = self.session.query(ReservationLifecycle).filter(
                ReservationLifecycle.user_id == user_id,
                ReservationLifecycle.resource_id == resource_id,
                ReservationLifecycle.request_date.isnot(None),
                ReservationLifecycle.approved_date.isnot(None),
                ReservationLifecycle.cancelled_date.is_(None),
                ReservationLifecycle.released_date.is_(None)
            ).first()

            if not reservation:
                logging.error(f"{LOG_PREFIX_DATABASE}No approved reservation found for User {user_id} on Resource {resource_id}")
                return False, None, "RESERVATION_NOT_FOUND", "No approved reservation found to release"

            # Release the reservation
            release_epoch = get_current_epoch()
            reservation.released_date = release_epoch

            # Find next queued user (not cancelled, not approved yet, requested after current reservation)
            next_reservation = self.session.query(ReservationLifecycle).filter(
                ReservationLifecycle.resource_id == resource_id,
                ReservationLifecycle.approved_date.is_(None),
                ReservationLifecycle.cancelled_date.is_(None),
                ReservationLifecycle.released_date.is_(None),
                ReservationLifecycle.request_date >= reservation.request_date
            ).order_by(ReservationLifecycle.request_date.asc()).first()

            # Auto-approve next user if exists
            if next_reservation:
                next_reservation.approved_date = release_epoch
                next_user = self.session.query(User).filter(User.id == next_reservation.user_id).first()
                logging.info(f"{LOG_PREFIX_DATABASE}Auto-approved next user: {next_reservation.user_id} ({next_user.name}) for Resource {resource_id}")
            self.session.commit()

            # Logging
            release_iso = epoch_to_iso8601(release_epoch)
            user_name = current_user['user_name']
            resource_name = reservation.resource.name
            logging.info(f"{LOG_PREFIX_DATABASE}Reservation released: User {user_id} ({user_name}) for Resource {resource_id} ({resource_name}) at {release_iso}")

            return True, reservation, None, None

    def get_active_reservations(self, resource_id):
        """
        Retrieve active reservations (not cancelled or released) for a specific resource ordered by request date.

        Args:
            resource_id (int): ID of the resource to get active reservations for. Required.

        Returns:
            list: List of ReservationLifecycle objects representing active reservations for the resource.

        Example:
            reservations = db.get_active_reservations(1)
            for r in reservations:
                status = "approved" if r.approved_date else "queued"
                print(f"Reservation {r.id}: {r.user.name} -> {r.resource.name} ({status})")
        """
        with self.lock:
            reservations = self.session.query(ReservationLifecycle).join(User).join(Resource).filter(
                ReservationLifecycle.resource_id == resource_id,
                ReservationLifecycle.cancelled_date.is_(None),
                ReservationLifecycle.released_date.is_(None)
            ).order_by(ReservationLifecycle.request_date.asc()).all()
            logging.info(f"{LOG_PREFIX_DATABASE}Retrieved {len(reservations)} active reservations for Resource {resource_id}")
            return reservations

