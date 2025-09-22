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


if __name__ == '__main__':
    reservia_app.run(host='0.0.0.0', port=5000, debug=True)