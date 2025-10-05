import logging
from flask import Blueprint, jsonify, current_app
from .base_view import BaseView
from ..constants import LOG_PREFIX_ENDPOINT
from ..database import Database

class IsAliveView(BaseView):
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/info/is_alive endpoint accessed")
        return jsonify({"status": "alive", "service": "Reservia"})

class GetVersionView(BaseView):
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/info/get_version endpoint accessed")
        return jsonify({"version": current_app.config['APP_CONFIG']['version']})

class InfoResourceList(BaseView):
    """Handles GET requests for retrieving all resources.

    Returns all resources in the system.

    Returns:
        tuple: JSON response with resources list and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X GET \
             http://localhost:5000/info/resources
    """
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/info/resources endpoint accessed")

        try:
            db = Database.get_instance()
            success, resources, error_code, error_msg = db.get_resources()

            if success:
                resource_list = []
                for r in resources:
                    resource_list.append({
                        "id": r.id,
                        "name": r.name,
                        "comment": r.comment
                    })

                return jsonify({
                    "message": "Resources retrieved successfully",
                    "resources": resource_list,
                    "count": len(resource_list)
                }), 200
            else:
                return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error retrieving resources: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class InfoUserList(BaseView):
    """Handles GET requests for retrieving all users (admin only).

    Returns all users in the system with id, name, email, and is_admin fields.
    Only accessible by admin users.

    Returns:
        tuple: JSON response with users list and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X GET -b cookies.txt \
             http://localhost:5000/info/users
    """
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/info/users endpoint accessed")

        try:
            db = Database.get_instance()
            success, users, error_code, error_msg = db.get_users()

            if success:
                return jsonify({
                    "message": "Users retrieved successfully",
                    "users": users,
                    "count": len(users)
                }), 200
            else:
                if error_code == "UNAUTHORIZED":
                    return jsonify({"error": error_msg}), 403
                else:
                    return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error retrieving users: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class InfoBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('info', __name__, url_prefix='/info')
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/is_alive', view_func=IsAliveView.as_view('is_alive'))
        self.blueprint.add_url_rule('/get_version', view_func=GetVersionView.as_view('get_version'))
        self.blueprint.add_url_rule('/resources', view_func=InfoResourceList.as_view('resource_list'), methods=['GET'])
        self.blueprint.add_url_rule('/users', view_func=InfoUserList.as_view('user_list'), methods=['GET'])

    def get_blueprint(self):
        return self.blueprint