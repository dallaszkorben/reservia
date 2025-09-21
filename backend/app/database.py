import os
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .constants import LOG_PREFIX_DATABASE

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

        logging.info(f"{LOG_PREFIX_DATABASE}Database initialized at {db_path}")

    def create_user(self, name, email):
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        logging.info(f"{LOG_PREFIX_DATABASE}User created: {name} ({email})")
        return user

    def get_users(self):
        users = self.session.query(User).all()
        logging.info(f"{LOG_PREFIX_DATABASE}Retrieved {len(users)} users")
        return users

    def create_resource(self, name, comment=None):
        resource = Resource(name=name, comment=comment)
        self.session.add(resource)
        self.session.commit()
        logging.info(f"{LOG_PREFIX_DATABASE}Resource created: {name}")
        return resource

    def get_resources(self):
        resources = self.session.query(Resource).all()
        logging.info(f"{LOG_PREFIX_DATABASE}Retrieved {len(resources)} resources")
        return resources