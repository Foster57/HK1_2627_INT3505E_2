import sys
from pathlib import Path
from flask import Flask, redirect

# Đảm bảo import được package src dù thực thi từ Week4 (python -m tasks.app) hay từ bên trong tasks/
tasks_root_dir = Path(__file__).resolve().parent
if str(tasks_root_dir) not in sys.path:
    sys.path.insert(0, str(tasks_root_dir))

# pyrefly: ignore [missing-import]
from flask_smorest import Api

from src.routes.tasks import blp as tasks_blueprint
from src.handlers.exception import register_error_handlers
from src.database.tasks_db import init_db

SERVER_CONFIG = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": True,
}


def create_app() -> Flask:
    """Hàm khởi tạo ứng dụng Flask và cấu hình OpenAPI / Swagger UI."""
    app = Flask(__name__)

    # Cấu hình OpenAPI 3.0.3 và Swagger UI tích hợp
    app.config.update(
        API_TITLE="Tasks Management API",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/",
        OPENAPI_JSON_PATH="openapi.json",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    )

    # Đăng ký Smorest API
    api = Api(app)
    api.register_blueprint(tasks_blueprint)

    # Đăng ký xử lý lỗi RFC 7807 Problem Details
    register_error_handlers(app)

    # Điều hướng tự động từ trang chủ sang tài liệu Swagger UI
    @app.route("/")
    def index():
        return redirect("/docs", code=302)

    return app


app = create_app()

if __name__ == "__main__":
    init_db()
    print(f"🚀 Server đang chạy tại http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
    print(f"📖 Swagger UI trực quan hóa tại http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}/docs")
    app.run(**SERVER_CONFIG)