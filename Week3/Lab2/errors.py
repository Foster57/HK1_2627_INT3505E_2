import logging
import traceback

from flask import jsonify, request
from werkzeug.exceptions import HTTPException


# =========================================================
# PROBLEM ERROR - Exception class theo RFC 7807
# =========================================================

class ProblemError(Exception):
    """
    Exception class trả về lỗi theo chuẩn RFC 7807 (Problem Details).

    Response body có dạng:
    {
        "type": "about:blank",
        "title": "Not Found",
        "status": 404,
        "detail": "User with id 999 not found",
        "instance": "/api/v1/users/999"
    }
    """

    def __init__(self, status, title, detail, type="about:blank", instance=None):
        """
        Args:
            status:   HTTP status code (ví dụ: 404, 400, 409)
            title:    Tên ngắn gọn của loại lỗi (ví dụ: "Not Found")
            detail:   Mô tả chi tiết lỗi cụ thể
            type:     URI định danh loại lỗi (mặc định "about:blank")
            instance: URI của request gây ra lỗi (tự lấy từ request nếu None)
        """
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type
        self.instance = instance

    def to_dict(self):
        """Chuyển đổi thành dict theo chuẩn RFC 7807."""
        return {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance or request.path
        }


# =========================================================
# ĐĂNG KÝ ERROR HANDLERS CHO FLASK APP
# =========================================================

def register_error_handlers(app):
    """Đăng ký tất cả error handlers cho Flask app."""

    logger = logging.getLogger(__name__)

    # ---------------------------------------------------------
    # Handler 1: ProblemError → problem+json
    # Xử lý các lỗi do developer chủ động raise
    # ---------------------------------------------------------
    @app.errorhandler(ProblemError)
    def handle_problem_error(error):
        """Xử lý ProblemError, trả về problem+json."""
        response = jsonify(error.to_dict())
        response.status_code = error.status
        response.content_type = "application/problem+json"
        return response

    # ---------------------------------------------------------
    # Handler 2: HTTPException → problem+json (fallback)
    # Xử lý các lỗi HTTP chuẩn (404 Not Found, 405 Method
    # Not Allowed, ...) mà Werkzeug/Flask tự raise
    # ---------------------------------------------------------
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Chuyển đổi HTTPException của Werkzeug sang problem+json."""
        body = {
            "type": "about:blank",
            "title": error.name,
            "status": error.code,
            "detail": error.description,
            "instance": request.path
        }

        response = jsonify(body)
        response.status_code = error.code
        response.content_type = "application/problem+json"
        return response

    # ---------------------------------------------------------
    # Handler 3: Exception → 500 problem+json (catch-all)
    # Xử lý mọi exception chưa bắt, KHÔNG lộ stack trace
    # cho client, chỉ log chi tiết server-side
    # ---------------------------------------------------------
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """
        Catch-all cho exception chưa bắt.
        - Client nhận message trung tính (không lộ chi tiết)
        - Server log đầy đủ stack trace để debug
        """
        # Log chi tiết server-side
        logger.error(
            "Unhandled exception at %s %s:\n%s",
            request.method,
            request.path,
            traceback.format_exc()
        )

        body = {
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred. Please try again later.",
            "instance": request.path
        }

        response = jsonify(body)
        response.status_code = 500
        response.content_type = "application/problem+json"
        return response
