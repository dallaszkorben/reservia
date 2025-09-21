from backend.app import create_app

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

app = create_app(config_dict)

if __name__ == '__main__':
    app.run(debug=True)