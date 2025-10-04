from flask import Blueprint, render_template, send_from_directory, current_app
from .base_view import BaseView

class HomeView(BaseView):
    def get(self):
        return render_template('index.html')

class HomeBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('home', __name__)
        self._register_routes()
    
    def _register_routes(self):
        self.blueprint.add_url_rule('/', view_func=HomeView.as_view('home'))
        # Explicit route for favicon.ico to ensure browsers can access it
        self.blueprint.add_url_rule('/favicon.ico', view_func=self._favicon)
    
    def _favicon(self):
        """Serve favicon.ico from static folder
        
        Flask doesn't always auto-serve favicon.ico from static folder,
        so we create an explicit route to handle browser requests for /favicon.ico
        """
        return send_from_directory(current_app.static_folder, 'favicon.ico')
    
    def get_blueprint(self):
        return self.blueprint