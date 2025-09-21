from flask import Blueprint, jsonify

info_bp = Blueprint('info', __name__, url_prefix='/info')

@info_bp.route('/is_alive')
def is_alive():
    return jsonify({"status": "alive", "service": "Reservia"})