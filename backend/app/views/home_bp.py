from flask import Blueprint
from .base_view import BaseView

class HomeView(BaseView):
    def get(self):
        return "Reservia - Resource Reservation Management System"

class HomeBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('home', __name__)
        self._register_routes()
    
    def _register_routes(self):
        self.blueprint.add_url_rule('/', view_func=HomeView.as_view('home'))
    
    def get_blueprint(self):
        return self.blueprint