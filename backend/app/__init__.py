from .application import ReserviaApp

def create_app(config_dict=None):
    """Factory function for backward compatibility"""
    reservia_app = ReserviaApp(config_dict)
    return reservia_app.create_app()