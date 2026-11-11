from flask.views import MethodView
from flask_smorest import Blueprint
from product_api.api.schemas import HealthSchema
from product_api.extensions import db
from sqlalchemy import text

blp = Blueprint("health", __name__, url_prefix="/health", description="Health check operations")


@blp.route("/")
class HealthCheck(MethodView):
    @blp.response(200, HealthSchema)
    def get(self):
        """Check API and database health status"""
        db_status = "healthy"
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db_status = "unhealthy"

        return {
            "status": "ok",
            "version": "1.0.0",
            "database": db_status,
        }

