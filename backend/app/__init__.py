from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../../frontend/templates', static_folder='../../frontend/static')
    
    from .views.info import info_bp
    app.register_blueprint(info_bp)
    
    return app