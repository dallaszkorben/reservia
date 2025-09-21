from backend.app.application import ReserviaApp

config_dict = {
    'app_name': 'reservia',
    'version': '1.0.0',
    'log': {
        'log_name': 'reservia.log',
        'level': 'DEBUG',
        'backupCount': 5
    },
    'database': {
        'name': 'reservia.db'
    }
}

# Create application instance - Apache will use this 'app' variable
reservia_app = ReserviaApp(config_dict)
app = reservia_app.create_app()

if __name__ == '__main__':
    app.run(debug=True)