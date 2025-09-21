import logging
from flask import Blueprint, jsonify, request, current_app
from .base_view import BaseView
from ..constants import LOG_PREFIX_ENDPOINT
from ..database import Database

class AdminUserAdd(BaseView):
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/admin/user/add endpoint accessed")
        
        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({"error": "Missing required fields: name, email"}), 400
        
        name = data['name']
        email = data['email']
        
        try:
            db = Database.get_instance()
            user = db.create_user(name, email)
            return jsonify({"message": "User created successfully", "user_id": user.id}), 201
        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error creating user: {str(e)}")
            return jsonify({"error": "Failed to create user"}), 500

class AdminBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('admin', __name__, url_prefix='/admin')
        self._register_routes()
    
    def _register_routes(self):
        self.blueprint.add_url_rule('/user/add', view_func=AdminUserAdd.as_view('user_add'), methods=['POST'])
    
    def get_blueprint(self):
        return self.blueprint