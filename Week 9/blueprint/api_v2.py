from flask import Blueprint
from .users_data import get_user

bp = Blueprint("v2", __name__, url_prefix="/users")

@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u:
        return {"error": "nf"}, 404
    return {
        "id": uid,
        "first_name": u["first_name"],
        "last_name": u["last_name"],
        "email": u["email"],
    }

@bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    uid = max(USERS) + 1
    USERS[uid] = {k: data[k] for k in ("first_name", "last_name", "email")}
    return {"id": uid, **USERS[uid]}, 201