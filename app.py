import argparse
from backend.app.application import ReserviaApp
from backend.config.config import CONFIG

def parse_arguments():
    """Parse command-line arguments for server configuration."""
    parser = argparse.ArgumentParser(
        description="Reservia - Resource Reservation Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
              python app.py                    # Start with default settings (auth enabled)
              python app.py --no-auth          # Start with authentication disabled
                    """
    )

    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable authentication requirement (default: authentication enabled)"
    )

    return parser.parse_args()

# Parse command-line arguments
args = parse_arguments()

# Add version and command-line overrides to config
config_dict = CONFIG.copy()
config_dict['version'] = '1.0.0'

# Support both command-line args and environment variables
import os
no_auth = args.no_auth or os.getenv('RESERVIA_NO_AUTH', '').lower() in ('1', 'true', 'yes')
config_dict['need_auth'] = not no_auth

# Create application instance - Apache will use this 'app' variable
reservia_app = ReserviaApp(config_dict)


if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    reservia_app.run(host='0.0.0.0', port=5000, debug=debug_mode)