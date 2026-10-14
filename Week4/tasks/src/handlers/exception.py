from __future__ import annotations

import logging
import uuid
from typing import Any, Optional
from flask import Flask, jsonify, request, Response
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)
DEFAULT_ERROR_BASE = "https://httpstatuses.com"


class ApiProblem(Exception):
    """
    Ngoại lệ chuẩn hóa cấu trúc lỗi theo RFC 7807 (Problem Details for HTTP APIs).
    Mime-type: application/problem+json
    """

    def __init__(
        self,
        status: int,
        title: str,
        detail: Optional[str] = None,
        type_uri: Optional[str] = None,
        instance: Optional[str] = None,
        **extra_fields: Any,
    ) -> None:
        super().__init__(detail or title)
        self.status = status
        self.title = title
        self.detail = detail
        self.type_uri = type_uri or f"{DEFAULT_ERROR_BASE}/{status}"
        self.instance = instance or request.path
        self.trace_id = str(uuid.uuid4())
        self.extra_fields = extra_fields

    def to_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "type": self.type_uri,
            "title": self.title,
            "status": self.status,
            "instance": self.instance,
            "trace_id": self.trace_id,
        }
        if self.detail:
            body["detail"] = self.detail
        body.update(self.extra_fields)
        return body

    def to_response(self) -> Response:
        resp = jsonify(self.to_dict())
        resp.status_code = self.status
        resp.headers["Content-Type"] = "application/problem+json"
        return resp

    @classmethod
    def from_http_exception(cls, ex: HTTPException) -> "ApiProblem":
        code = ex.code or 500
        return cls(
            status=code,
            title=ex.name,
            detail=ex.description,
            type_uri=f"{DEFAULT_ERROR_BASE}/{code}",
        )


def register_error_handlers(app: Flask) -> None:
    """Đăng ký các bộ bắt lỗi toàn cục cho ứng dụng Flask."""

    @app.errorhandler(ApiProblem)
    def handle_api_problem(err: ApiProblem) -> Response:
        return err.to_response()

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException) -> Response:
        # Nếu đã có body JSON từ flask_smorest / webargs
        messages = getattr(err, "data", {}).get("messages")
        problem = ApiProblem.from_http_exception(err)
        if messages:
            problem.extra_fields["errors"] = messages
        return problem.to_response()

    @app.errorhandler(Exception)
    def handle_unhandled_exception(err: Exception) -> Response:
        problem = ApiProblem(
            status=500,
            title="Internal Server Error",
            detail="Máy chủ gặp sự cố không mong muốn trong quá trình xử lý.",
            type_uri=f"{DEFAULT_ERROR_BASE}/500",
        )
        logger.exception(
            "Lỗi hệ thống chưa xử lý | trace_id=%s | method=%s | path=%s | error=%s",
            problem.trace_id,
            request.method,
            request.path,
            str(err),
        )
        return problem.to_response()