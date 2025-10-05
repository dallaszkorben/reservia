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
        self.blueprint.add_url_rule('/user/modify', view_func=AdminUserModify.as_view('user_modify'), methods=['POST'])
        self.blueprint.add_url_rule('/resource/add', view_func=AdminResourceAdd.as_view('resource_add'), methods=['POST'])
        self.blueprint.add_url_rule('/resource/modify', view_func=AdminResourceModify.as_view('resource_modify'), methods=['POST'])

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


class AdminUserModify(BaseView):
    """
    User modification endpoint (admin can modify any user, user can modify self)

    Usage:
    curl -H "Content-Type: application/json" -X POST -b cookies.txt \
         -d '{"user_id": 2, "email": "new@example.com", "password": "newpass123"}' \
         http://localhost:5000/admin/user/modify
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/admin/user/modify endpoint accessed")

        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({"error": "Missing required field: user_id"}), 400

        user_id = data['user_id']
        email = data.get('email')
        password = data.get('password')

        if not email and not password:
            return jsonify({"error": "At least one field must be provided: email, password"}), 400

        try:
            db = Database.get_instance()
            success, user, error_code, error_msg = db.modify_user(user_id, email, password)
            if success:
                return jsonify({"message": "User modified successfully", "user_id": user.id}), 200
            else:
                if error_code == "UNAUTHORIZED":
                    return jsonify({"error": error_msg}), 403
                elif error_code == "USER_NOT_FOUND":
                    return jsonify({"error": error_msg}), 404
                elif error_code == "EMAIL_EXISTS":
                    return jsonify({"error": error_msg}), 409
                return jsonify({"error": error_msg}), 400
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error modifying user: {str(e)}")
            return jsonify({"error": "Failed to modify user"}), 500


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


class AdminResourceModify(BaseView):
    """
    Resource modification endpoint (admin only)

    Usage:
    curl -H "Content-Type: application/json" -X POST -b cookies.txt \
         -d '{"resource_id": 1, "name": "New Room Name", "comment": "Updated description"}' \
         http://localhost:5000/admin/resource/modify
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/admin/resource/modify endpoint accessed")

        data = request.get_json()
        if not data or 'resource_id' not in data:
            return jsonify({"error": "Missing required field: resource_id"}), 400

        resource_id = data['resource_id']
        name = data.get('name')
        comment = data.get('comment')

        if not name and not comment:
            return jsonify({"error": "At least one field must be provided: name, comment"}), 400

        try:
            db = Database.get_instance()
            success, resource, error_code, error_msg = db.modify_resource(resource_id, name, comment)
            if success:
                return jsonify({"message": "Resource modified successfully", "resource_id": resource.id}), 200
            else:
                if error_code == "UNAUTHORIZED":
                    return jsonify({"error": error_msg}), 403
                elif error_code == "RESOURCE_NOT_FOUND":
                    return jsonify({"error": error_msg}), 404
                elif error_code == "RESOURCE_EXISTS":
                    return jsonify({"error": error_msg}), 409
                return jsonify({"error": error_msg}), 400
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error modifying resource: {str(e)}")
            return jsonify({"error": "Failed to modify resource"}), 500




