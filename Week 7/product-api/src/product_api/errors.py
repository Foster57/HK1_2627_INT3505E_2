from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """Base API Exception."""

    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["status_code"] = self.status_code
        return rv


class NotFoundError(APIError):
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)


class BadRequestError(APIError):
    def __init__(self, message="Bad request", payload=None):
        super().__init__(message, status_code=400, payload=payload)


def register_error_handlers(app):
    """Register custom error handlers for the Flask app."""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = jsonify({
            "status_code": error.code,
            "message": error.description,
        })
        response.status_code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        if app.config.get("DEBUG"):
            raise error
        response = jsonify({
            "status_code": 500,
            "message": "An internal server error occurred",
        })
        response.status_code = 500
        return response

