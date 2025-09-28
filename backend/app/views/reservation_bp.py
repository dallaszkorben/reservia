import logging
from flask import Blueprint, jsonify, request
from .base_view import BaseView
from ..constants import LOG_PREFIX_ENDPOINT
from ..database import Database
from ..utils import epoch_to_iso8601

class RequestReservationView(BaseView):
    """
    User reservation request endpoint (requires user login)

    Usage:
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
            reservation = db.request_reservation(resource_id)

            if reservation:
                return jsonify({
                    "message": "Reservation request successful",
                    "reservation_id": reservation.id,
                    "resource_id": reservation.resource_id,
                    "status": "approved" if reservation.approved_date else "requested"
                }), 201
            else:
                return jsonify({"error": "Failed to create reservation"}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in request_reservation: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class CancelReservationView(BaseView):
    """
    Cancel reservation endpoint (requires user login)

    Usage:
    curl -H "Content-Type: application/json" -X POST -b cookies.txt \
         -d '{"resource_id": 1}' \
         http://localhost:5000/reservation/cancel

    Success Response:
    {
        "message": "Reservation cancelled successfully",
        "reservation_id": <reservation_id>,
        "resource_id": <resource_id>,
        "cancelled_date": "<iso8601_datetime>"
    }

    Example Response:
    {
        "message": "Reservation cancelled successfully",
        "reservation_id": 2,
        "resource_id": 1,
        "cancelled_date": "2023-12-21T10:45:30+01:00"
    }

    Error Responses:
    - 400: {"error": "JSON data required"}
    - 400: {"error": "resource_id is required"}
    - 400: {"error": "Failed to cancel reservation"}
    - 500: {"error": "Internal server error"}
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/cancel endpoint accessed")

        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON data required"}), 400

            resource_id = data.get('resource_id')
            if not resource_id:
                return jsonify({"error": "resource_id is required"}), 400

            db = Database.get_instance()
            reservation = db.cancel_reservation(resource_id)

            if reservation:
                return jsonify({
                    "message": "Reservation cancelled successfully",
                    "reservation_id": reservation.id,
                    "resource_id": reservation.resource_id,
                    "cancelled_date": epoch_to_iso8601(reservation.cancelled_date)
                }), 200
            else:
                return jsonify({"error": "Failed to cancel reservation"}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in cancel_reservation: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500




class ReleaseReservationView(BaseView):
    """
    Release reservation endpoint (requires user login)

    Usage:
    curl -H "Content-Type: application/json" -X POST -b cookies.txt \
         -d '{"resource_id": 1}' \
         http://localhost:5000/reservation/release

    Success Response:
    {
        "message": "Reservation released successfully",
        "reservation_id": <reservation_id>,
        "resource_id": <resource_id>,
        "released_date": "<iso8601_datetime>"
    }

    Example Response:
    {
        "message": "Reservation released successfully",
        "reservation_id": 1,
        "resource_id": 1,
        "released_date": "2023-12-21T11:00:15+01:00"
    }

    Error Responses:
    - 400: {"error": "JSON data required"}
    - 400: {"error": "resource_id is required"}
    - 400: {"error": "Failed to release reservation"}
    - 500: {"error": "Internal server error"}
    """
    def post(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/release endpoint accessed")

        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "JSON data required"}), 400

            resource_id = data.get('resource_id')
            if not resource_id:
                return jsonify({"error": "resource_id is required"}), 400

            db = Database.get_instance()
            reservation = db.release_reservation(resource_id)

            if reservation:
                return jsonify({
                    "message": "Reservation released successfully",
                    "reservation_id": reservation.id,
                    "resource_id": reservation.resource_id,
                    "released_date": epoch_to_iso8601(reservation.released_date)
                }), 200
            else:
                return jsonify({"error": "Failed to release reservation"}), 400

        except Exception as e:
            logging.error(f"{LOG_PREFIX_ENDPOINT}Error in release_reservation: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500


class GetActiveReservationsView(BaseView):
    """
    Get active reservations endpoint (requires user login)

    Usage:
    curl -H "Content-Type: application/json" -X GET -b cookies.txt \
         -d '{}' \
         http://localhost:5000/reservation/active

    General Output Format:
    {
        "message": "Active reservations retrieved successfully",
        "reservations": [
            {
                "id": <reservation_id>,
                "user_id": <user_id>,
                "user_name": "<user_name>",
                "resource_id": <resource_id>,
                "resource_name": "<resource_name>",
                "request_date": "<iso8601_datetime>",
                "approved_date": "<iso8601_datetime_or_null>",
                "status": "approved|requested"
            }
        ],
        "count": <number_of_reservations>
    }

    Example Output:
    {
        "message": "Active reservations retrieved successfully",
        "reservations": [
            {
                "id": 1,
                "user_id": 2,
                "user_name": "john_doe",
                "resource_id": 1,
                "resource_name": "Meeting Room A",
                "request_date": "2023-12-21T10:30:56+01:00",
                "approved_date": "2023-12-21T10:30:56+01:00",
                "status": "approved"
            },
            {
                "id": 2,
                "user_id": 3,
                "user_name": "jane_smith",
                "resource_id": 1,
                "resource_name": "Meeting Room A",
                "request_date": "2023-12-21T10:31:40+01:00",
                "approved_date": null,
                "status": "requested"
            }
        ],
        "count": 2
    }
    """
    def get(self):
        logging.info(f"{LOG_PREFIX_ENDPOINT}/reservation/active endpoint accessed")

        try:
            db = Database.get_instance()
            current_user = db.get_current_user()

            if not current_user:
                return jsonify({"error": "Authentication required"}), 401

            reservations = db.get_active_reservations()

            reservation_list = []
            for r in reservations:
                reservation_list.append({
                    "id": r.id,
                    "user_id": r.user_id,
                    "user_name": r.user.name,
                    "resource_id": r.resource_id,
                    "resource_name": r.resource.name,
                    "request_date": epoch_to_iso8601(r.request_date),
                    "approved_date": epoch_to_iso8601(r.approved_date) if r.approved_date else None,
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

    def get_blueprint(self):
        return self.blueprint