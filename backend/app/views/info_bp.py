import logging
from flask import Blueprint, jsonify, current_app
from .base_view import BaseView
from ..constants import LOG_PREFIX_ENDPOINT

class IsAliveView(BaseView):
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/info/is_alive endpoint accessed")
        return jsonify({"status": "alive", "service": "Reservia"})

class GetVersionView(BaseView):
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/info/get_version endpoint accessed")
        return jsonify({"version": current_app.config['APP_CONFIG']['version']})

class InfoBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('info', __name__, url_prefix='/info')
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/is_alive', view_func=IsAliveView.as_view('is_alive'))
        self.blueprint.add_url_rule('/get_version', view_func=GetVersionView.as_view('get_version'))

    def get_blueprint(self):
        return self.blueprint