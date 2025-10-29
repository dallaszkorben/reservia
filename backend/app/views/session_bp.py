import logging
from flask import Blueprint, jsonify, request, session, current_app
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
        self.blueprint.add_url_rule('/status', view_func=SessionStatus.as_view('status'), methods=['GET'])

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
        if not data or 'name' not in data:
            return jsonify({"error": "Missing required field: name"}), 400

        name = data['name']
        password = data.get('password')  # Optional in no-auth mode
        
        # Check if auth is required
        no_auth = not current_app.config['APP_CONFIG'].get('need_auth', True)
        if not no_auth and not password:
            return jsonify({"error": "Password required when authentication is enabled"}), 400

        try:
            db = Database.get_instance()
            success, user, error_code, error_msg = db.login(name, password)
            if success:
                return jsonify({"message": "Login successful", "user_name": user.name}), 200
            else:
                return jsonify({"error": error_msg}), 401
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
            success, _, error_code, error_msg = db.logout()
            response = jsonify({"message": "Logout successful" if success else error_msg})
            if success:
                # Clear the session cookie by setting it to expire
                response.set_cookie('session', '', expires=0)
            return response, 200
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error during logout: {str(e)}")
            return jsonify({"error": "Logout failed"}), 500


class SessionStatus(BaseView):
    """
    Check current session status endpoint

    Usage:
    curl -b cookies.txt http://localhost:5000/session/status
    """
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/session/status endpoint accessed")

        if 'logged_in_user' in session:
            user_data = session['logged_in_user']
            return jsonify({
                'logged_in': True,
                'user_id': user_data.get('user_id'),
                'user_email': user_data.get('user_email'),
                'user_name': user_data.get('user_name'),
                'role': user_data.get('role')
            }), 200
        else:
            return jsonify({'logged_in': False}), 401