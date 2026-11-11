import os
from flask import Flask, redirect
from product_api.api import health_blp, orders_blp, products_blp
from product_api.config import config_by_name
from product_api.errors import register_error_handlers
from product_api.extensions import api, db


def create_app(config_name=None):
    """Application factory for Flask product-api."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    api.init_app(app)

    # Register blueprints with flask-smorest
    api.register_blueprint(health_blp)
    api.register_blueprint(products_blp)
    api.register_blueprint(orders_blp)

    # Register error handlers
    register_error_handlers(app)

    # Root redirect to swagger docs
    @app.route("/")
    def index():
        return redirect(app.config.get("OPENAPI_SWAGGER_UI_PATH", "/docs"))

    # Auto-create tables for development / testing
    with app.app_context():
        db.create_all()

    return app

