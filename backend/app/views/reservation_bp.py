import logging
from flask import Blueprint, jsonify, request
from .base_view import BaseView
from ..constants import LOG_PREFIX_ENDPOINT
from ..database import Database
from ..utils import epoch_to_iso8601
from ...config.config import CONFIG

class RequestReservationView(BaseView):
    """Handles POST requests for creating new reservation requests.

    Requires user authentication. Creates a new reservation request for the specified resource.
    If the resource is available, the request is auto-approved.
    Users cannot make duplicate requests for the same resource if they already have an active reservation.

    Returns:
        tuple: JSON response with reservation details and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X POST -b cookies.txt \
             -d '{"resource_id": 1}' \
             http://localhost:5000/reservation/request
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/request endpoint accessed")

        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON data required"}), 400

            resource_id = data.get('resource_id')
            if not resource_id:
                return jsonify({"error": "resource_id is required"}), 400

            db = Database.get_instance()
            success, reservation, error_code, error_msg = db.request_reservation(resource_id)

            if success:
                return jsonify({
                    "message": "Reservation request successful",
                    "reservation_id": reservation.id,
                    "resource_id": reservation.resource_id,
                    "status": "approved" if reservation.approved_date else "requested"
                }), 201
            else:
                if error_code == "AUTH_REQUIRED":
                    return jsonify({"error": error_msg}), 401
                elif error_code == "RESOURCE_NOT_FOUND":
                    return jsonify({"error": error_msg}), 404
                elif error_code == "DUPLICATE_RESERVATION":
                    return jsonify({"error": error_msg}), 409
                return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in request_reservation: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class CancelReservationView(BaseView):
    """Handles POST requests for cancelling existing reservation requests.

    Requires user authentication. Cancels the user's active reservation request
    for the specified resource by setting the cancelled_date.

    Returns:
        tuple: JSON response with cancellation details and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X POST -b cookies.txt \
             -d '{"resource_id": 1}' \
             http://localhost:5000/reservation/cancel
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/cancel endpoint accessed")

        try:
            # Check authentication at endpoint level
            db = Database.get_instance()
            current_user = db.get_current_user()
            if not current_user:
                return jsonify({"error": "Authentication required"}), 401

            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON data required"}), 400

            resource_id = data.get('resource_id')
            if not resource_id:
                return jsonify({"error": "resource_id is required"}), 400

            user_id = current_user['user_id']
            success, reservation, error_code, error_msg = db.cancel_reservation(resource_id, user_id)

            if success:
                return jsonify({
                    "message": "Reservation cancelled successfully",
                    "reservation_id": reservation.id,
                    "resource_id": reservation.resource_id,
                    "cancelled_date": epoch_to_iso8601(reservation.cancelled_date)
                }), 200
            else:
                if error_code == "RESERVATION_NOT_FOUND":
                    return jsonify({"error": error_msg}), 404
                return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in cancel_reservation: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500




class ReleaseReservationView(BaseView):
    """Handles POST requests for releasing approved reservations.

    Requires user authentication. Releases the user's approved reservation
    for the specified resource and auto-approves the next queued user.

    Returns:
        tuple: JSON response with release details and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X POST -b cookies.txt \
             -d '{"resource_id": 1}' \
             http://localhost:5000/reservation/release
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/release endpoint accessed")

        try:
            # Check authentication at endpoint level
            db = Database.get_instance()
            current_user = db.get_current_user()
            if not current_user:
                return jsonify({"error": "Authentication required"}), 401

            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON data required"}), 400

            resource_id = data.get('resource_id')
            if not resource_id:
                return jsonify({"error": "resource_id is required"}), 400

            user_id = current_user['user_id']
            success, reservation, error_code, error_msg = db.release_reservation(resource_id, user_id)

            if success:
                return jsonify({
                    "message": "Reservation released successfully",
                    "reservation_id": reservation.id,
                    "resource_id": reservation.resource_id,
                    "released_date": epoch_to_iso8601(reservation.released_date)
                }), 200
            else:
                if error_code == "RESERVATION_NOT_FOUND":
                    return jsonify({"error": error_msg}), 404
                return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in release_reservation: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class KeepAliveReservationView(BaseView):
    """Handles POST requests for keeping alive approved reservations.

    Requires user authentication. Updates the valid_until_date for the user's
    approved reservation by adding approved_keep_alive_sec to current time.

    Returns:
        tuple: JSON response with keep alive details and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X POST -b cookies.txt \
             -d '{"resource_id": 1}' \
             http://localhost:5000/reservation/keep_alive
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/keep_alive endpoint accessed")

        try:
            # Check authentication at endpoint level
            db = Database.get_instance()
            current_user = db.get_current_user()
            if not current_user:
                return jsonify({"error": "Authentication required"}), 401

            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON data required"}), 400

            resource_id = data.get('resource_id')
            if not resource_id:
                return jsonify({"error": "resource_id is required"}), 400

            user_id = current_user['user_id']
            keep_alive_seconds = CONFIG['approved_keep_alive_sec']
            success, reservation, error_code, error_msg = db.keep_alive_reservation(resource_id, user_id, keep_alive_seconds)

            if success:
                return jsonify({
                    "message": "Reservation kept alive successfully",
                    "reservation_id": reservation.id,
                    "resource_id": reservation.resource_id,
                    "valid_until_date": epoch_to_iso8601(reservation.valid_until_date)
                }), 200
            else:
                if error_code == "RESERVATION_NOT_FOUND":
                    return jsonify({"error": error_msg}), 404
                return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in keep_alive_reservation: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class GetActiveReservationsView(BaseView):
    """Handles GET requests for retrieving active reservations for a specific resource.

    Requires user authentication and resource_id query parameter. Returns non-cancelled,
    non-released reservations for the specified resource with user and resource details.

    Returns:
        tuple: JSON response with reservations list and HTTP status code

    Example:
        curl -H "Content-Type: application/json" -X GET -b cookies.txt \
             "http://localhost:5000/reservation/active?resource_id=1"
    """
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/active endpoint accessed")

        try:
            db = Database.get_instance()
            current_user = db.get_current_user()

            if not current_user:
                return jsonify({"error": "Authentication required"}), 401

            resource_id = request.args.get('resource_id')
            if not resource_id:
                return jsonify({"error": "resource_id parameter is required"}), 400

            try:
                resource_id = int(resource_id)
            except ValueError:
                return jsonify({"error": "resource_id must be a valid integer"}), 400

            reservations = db.get_active_reservations(resource_id)

            reservation_list = []
            for r in reservations:
#                # Check if relationships are loaded properly
#                if not r.user or not r.resource:
#                    logging.error(f"{LOG_PREFIX_ENDPOINT}Missing user or resource relationship for reservation {r.id}")
#                    continue

                reservation_list.append({
                    "id": r.id,
                    "user_id": r.user_id,
                    "user_name": r.user.name,
                    "resource_id": r.resource_id,
                    "resource_name": r.resource.name,
                    "request_date": epoch_to_iso8601(r.request_date),
                    "approved_date": epoch_to_iso8601(r.approved_date) if r.approved_date else None,
                    "valid_until_date": r.valid_until_date,
                    "status": "approved" if r.approved_date else "requested"
                })

            return jsonify({
                "message": "Active reservations retrieved successfully",
                "reservations": reservation_list,
                "count": len(reservation_list)
            }), 200

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in get_active_reservations: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class ReservationBlueprintManager:
    def __init__(self):
        self.blueprint = Blueprint('reservation', __name__, url_prefix='/reservation')
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/request', view_func=RequestReservationView.as_view('request'))
        self.blueprint.add_url_rule('/active', view_func=GetActiveReservationsView.as_view('active'))
        self.blueprint.add_url_rule('/cancel', view_func=CancelReservationView.as_view('cancel'))
        self.blueprint.add_url_rule('/release', view_func=ReleaseReservationView.as_view('release'))
        self.blueprint.add_url_rule('/keep_alive', view_func=KeepAliveReservationView.as_view('keep_alive'))

    def get_blueprint(self):
        return self.blueprint