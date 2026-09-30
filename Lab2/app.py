import logging

from flask import Flask, jsonify, request
from data import users, posts
from errors import ProblemError, register_error_handlers


# =========================================================
# KHỞI TẠO APP + LOGGING
# =========================================================

app = Flask(__name__)

# Cấu hình logging để xem chi tiết lỗi server-side
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Đăng ký error handlers (problem+json)
register_error_handlers(app)


# =========================================================
# HELPER
# =========================================================

def get_next_id(collection):
    """Tạo ID mới cho collection."""
    return max(collection.keys(), default=0) + 1


# =========================================================
# USERS - Sử dụng ProblemError thay cho jsonify lỗi thủ công
# =========================================================

@app.route("/api/v1/users", methods=["GET"])
def get_users():
    """Lấy danh sách users."""
    return jsonify(list(users.values()))


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """Tạo user mới."""
    data = request.get_json()

    if not data or "username" not in data or "email" not in data:
        raise ProblemError(
            status=400,
            title="Bad Request",
            detail="Missing required fields: username, email"
        )

    new_id = get_next_id(users)

    user = {
        "id": new_id,
        "username": data["username"],
        "email": data["email"]
    }

    users[new_id] = user

    return jsonify(user), 201


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Lấy 1 user theo ID."""
    user = users.get(user_id)

    if not user:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"User with id {user_id} not found"
        )

    return jsonify(user)


@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
def replace_user(user_id):
    """Thay thế toàn bộ user."""
    if user_id not in users:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"User with id {user_id} not found"
        )

    data = request.get_json()

    if not data or "username" not in data or "email" not in data:
        raise ProblemError(
            status=400,
            title="Bad Request",
            detail="Missing required fields: username, email"
        )

    users[user_id] = {
        "id": user_id,
        "username": data["username"],
        "email": data["email"]
    }

    return jsonify(users[user_id])


@app.route("/api/v1/users/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    """Cập nhật 1 phần user."""
    if user_id not in users:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"User with id {user_id} not found"
        )

    data = request.get_json()

    if "username" in data:
        users[user_id]["username"] = data["username"]

    if "email" in data:
        users[user_id]["email"] = data["email"]

    return jsonify(users[user_id])


@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Xóa user."""
    if user_id not in users:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"User with id {user_id} not found"
        )

    del users[user_id]

    return "", 204


# =========================================================
# POSTS - Sử dụng ProblemError
# =========================================================

@app.route("/api/v1/posts", methods=["GET"])
def get_posts():
    """Lấy danh sách posts."""
    return jsonify(list(posts.values()))


@app.route("/api/v1/posts", methods=["POST"])
def create_post():
    """Tạo post mới."""
    data = request.get_json()

    if not data or "title" not in data or "content" not in data or "author_id" not in data:
        raise ProblemError(
            status=400,
            title="Bad Request",
            detail="Missing required fields: title, content, author_id"
        )

    author_id = data["author_id"]

    if author_id not in users:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"Author with id {author_id} not found"
        )

    new_id = get_next_id(posts)

    post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
        "author_id": author_id
    }

    posts[new_id] = post

    return jsonify(post), 201


@app.route("/api/v1/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    """Lấy 1 post."""
    post = posts.get(post_id)

    if not post:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"Post with id {post_id} not found"
        )

    return jsonify(post)


@app.route("/api/v1/posts/<int:post_id>", methods=["PUT"])
def replace_post(post_id):
    """Thay thế toàn bộ post."""
    if post_id not in posts:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"Post with id {post_id} not found"
        )

    data = request.get_json()

    if not data or "title" not in data or "content" not in data or "author_id" not in data:
        raise ProblemError(
            status=400,
            title="Bad Request",
            detail="Missing required fields: title, content, author_id"
        )

    posts[post_id] = {
        "id": post_id,
        "title": data["title"],
        "content": data["content"],
        "author_id": data["author_id"]
    }

    return jsonify(posts[post_id])


@app.route("/api/v1/posts/<int:post_id>", methods=["PATCH"])
def update_post(post_id):
    """Cập nhật 1 phần post."""
    if post_id not in posts:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"Post with id {post_id} not found"
        )

    data = request.get_json()

    if "title" in data:
        posts[post_id]["title"] = data["title"]

    if "content" in data:
        posts[post_id]["content"] = data["content"]

    return jsonify(posts[post_id])


@app.route("/api/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Xóa post."""
    if post_id not in posts:
        raise ProblemError(
            status=404,
            title="Not Found",
            detail=f"Post with id {post_id} not found"
        )

    del posts[post_id]

    return "", 204


# =========================================================
# ROUTE TEST: Gây lỗi 500 (unhandled exception)
# =========================================================

@app.route("/api/v1/test/crash", methods=["GET"])
def test_crash():
    """Route test gây ra unhandled exception để kiểm tra handler 500."""
    raise ZeroDivisionError("Test crash: intentional unhandled exception")
    return jsonify({"message": "This will never be reached"})


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
