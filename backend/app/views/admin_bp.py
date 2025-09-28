import logging
from flask import Blueprint, jsonify, request, current_app
from .base_view import BaseView
from ..constants import LOG_PREFIX_ENDPOINT
from ..database import Database


class AdminBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('admin', __name__, url_prefix='/admin')
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/user/add', view_func=AdminUserAdd.as_view('user_add'), methods=['POST'])
        self.blueprint.add_url_rule('/resource/add', view_func=AdminResourceAdd.as_view('resource_add'), methods=['POST'])
        self.blueprint.add_url_rule('/resources', view_func=AdminResourceList.as_view('resource_list'), methods=['GET'])

    def get_blueprint(self):
        return self.blueprint


class AdminUserAdd(BaseView):
    """
    Admin user creation endpoint (requires admin login)

    Usage:
    curl -H "Content-Type: application/json" -X POST -b cookies.txt \
         -d '{"name": "John Doe", "email": "john@example.com", "password": "password123"}' \
         http://localhost:5000/admin/user/add
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/admin/user/add endpoint accessed")

        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Missing required fields: name, email, password"}), 400

        name = data['name']
        email = data['email']
        password = data['password']

        try:
            db = Database.get_instance()
            success, user, error_code, error_msg = db.create_user(name, email, password)
            if success:
                return jsonify({"message": "User created successfully", "user_id": user.id}), 201
            else:
                if error_code == "UNAUTHORIZED":
                    return jsonify({"error": error_msg}), 403
                elif error_code in ["EMAIL_EXISTS", "USERNAME_EXISTS"]:
                    return jsonify({"error": error_msg}), 409
                return jsonify({"error": error_msg}), 400
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error creating user: {str(e)}")
            return jsonify({"error": "Failed to create user"}), 500


class AdminResourceAdd(BaseView):
    """
    Admin resource creation endpoint (requires admin login)

    Usage:
    curl -H "Content-Type: application/json" -X POST -b cookies.txt \
         -d '{"name": "Meeting Room", "comment": "Conference room for 10 people"}' \
         http://localhost:5000/admin/resource/add
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/admin/resource/add endpoint accessed")

        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Missing required field: name"}), 400

        name = data['name']
        comment = data.get('comment')

        try:
            db = Database.get_instance()
            success, resource, error_code, error_msg = db.create_resource(name, comment)
            if success:
                return jsonify({"message": "Resource created successfully", "resource_id": resource.id}), 201
            else:
                if error_code == "UNAUTHORIZED":
                    return jsonify({"error": error_msg}), 403
                elif error_code == "RESOURCE_EXISTS":
                    return jsonify({"error": error_msg}), 409
                return jsonify({"error": error_msg}), 400
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error creating resource: {str(e)}")
            return jsonify({"error": "Failed to create resource"}), 500


class AdminResourceList(BaseView):
    """Handles GET requests for retrieving all resources.

    Requires admin authentication. Returns all resources in the system.

    Returns:
        tuple: JSON response with resources list and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X GET -b cookies.txt \
             http://localhost:5000/admin/resources
    """
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/admin/resources endpoint accessed")

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
                if error_code == "UNAUTHORIZED":
                    return jsonify({"error": error_msg}), 403
                return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error retrieving resources: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

