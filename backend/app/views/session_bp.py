import logging
from flask import Blueprint, jsonify, request
from .base_view import BaseView
from ..constants import LOG_PREFIX_ENDPOINT
from ..database import Database


class SessionBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('session', __name__, url_prefix='/session')
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/login', view_func=SessionLogin.as_view('login'), methods=['POST'])
        self.blueprint.add_url_rule('/logout', view_func=SessionLogout.as_view('logout'), methods=['POST'])

    def get_blueprint(self):
        return self.blueprint


class SessionLogin(BaseView):
    """
    User login endpoint

    Usage:
    curl -H "Content-Type: application/json" -X POST -c cookies.txt \
         -d '{"name": "admin", "password": "admin"}' \
         http://localhost:5000/session/login
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/session/login endpoint accessed")

        data = request.get_json()
        if not data or 'name' not in data or 'password' not in data:
            return jsonify({"error": "Missing required fields: name, password"}), 400

        name = data['name']
        password = data['password']

        try:
            db = Database.get_instance()
            user = db.login(name, password)
            if user:
                return jsonify({"message": "Login successful", "user_name": user.name}), 200
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error during login: {str(e)}")
            return jsonify({"error": "Login failed"}), 500


class SessionLogout(BaseView):
    """
    User logout endpoint

    Usage:
    curl -X POST -b cookies.txt http://localhost:5000/session/logout
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/session/logout endpoint accessed")

        try:
            db = Database.get_instance()
            success = db.logout()
            response = jsonify({"message": "Logout successful" if success else "No active session"})
            if success:
                # Clear the session cookie by setting it to expire
                response.set_cookie('session', '', expires=0)
            return response, 200
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error during logout: {str(e)}")
            return jsonify({"error": "Logout failed"}), 500