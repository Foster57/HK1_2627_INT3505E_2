# pyrefly: ignore [missing-import]
from flask import Flask, jsonify, request

app = Flask(__name__)

from data import users, profiles, posts, comments, tags, post_tags, following


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_next_id(collection):
    """Tạo ID mới cho collection."""
    return max(collection.keys(), default=0) + 1


def error_response(message, status_code):
    """Trả về response lỗi chuẩn."""
    return jsonify({"error": message}), status_code


# =========================================================
# RESOURCE: USERS (Collection + Item)
# ---------------------------------------------------------
# GET    /api/v1/users            → Lấy danh sách users
# POST   /api/v1/users            → Tạo user mới
# GET    /api/v1/users/:id        → Lấy 1 user
# PUT    /api/v1/users/:id        → Thay thế toàn bộ user
# PATCH  /api/v1/users/:id        → Cập nhật 1 phần user
# DELETE /api/v1/users/:id        → Xóa user
# =========================================================

@app.route("/api/v1/users", methods=["GET"])
def get_users():
    """Lấy danh sách tất cả users."""
    return jsonify(list(users.values()))


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """Tạo user mới."""
    data = request.get_json()

    if not data or "username" not in data or "email" not in data:
        return error_response("Missing required fields: username, email", 400)

    new_id = get_next_id(users)

    user = {
        "id": new_id,
        "username": data["username"],
        "email": data["email"]
    }

    users[new_id] = user
    following[new_id] = []  # Khởi tạo danh sách following rỗng

    return jsonify(user), 201


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Lấy thông tin 1 user theo ID."""
    user = users.get(user_id)

    if not user:
        return error_response("User not found", 404)

    return jsonify(user)


@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
def replace_user(user_id):
    """Thay thế toàn bộ thông tin user (PUT = full replace)."""
    if user_id not in users:
        return error_response("User not found", 404)

    data = request.get_json()

    if not data or "username" not in data or "email" not in data:
        return error_response("Missing required fields: username, email", 400)

    users[user_id] = {
        "id": user_id,
        "username": data["username"],
        "email": data["email"]
    }

    return jsonify(users[user_id])


@app.route("/api/v1/users/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    """Cập nhật 1 phần thông tin user (PATCH = partial update)."""
    if user_id not in users:
        return error_response("User not found", 404)

    data = request.get_json()

    if "username" in data:
        users[user_id]["username"] = data["username"]

    if "email" in data:
        users[user_id]["email"] = data["email"]

    return jsonify(users[user_id])


@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Xóa user và các dữ liệu liên quan."""
    if user_id not in users:
        return error_response("User not found", 404)

    # Xóa profile liên quan
    profiles.pop(user_id, None)

    # Xóa following liên quan
    following.pop(user_id, None)

    # Xóa user_id khỏi danh sách following của người khác
    for uid in following:
        if user_id in following[uid]:
            following[uid].remove(user_id)

    del users[user_id]

    return "", 204


# =========================================================
# SUB-RESOURCE: PROFILE (Singular - thuộc về User)
# ---------------------------------------------------------
# GET /api/v1/users/:id/profile   → Lấy profile của user
# PUT /api/v1/users/:id/profile   → Cập nhật profile
# =========================================================

@app.route("/api/v1/users/<int:user_id>/profile", methods=["GET"])
def get_profile(user_id):
    """Lấy profile của user."""
    if user_id not in users:
        return error_response("User not found", 404)

    profile = profiles.get(user_id)

    if not profile:
        return error_response("Profile not found", 404)

    return jsonify(profile)


@app.route("/api/v1/users/<int:user_id>/profile", methods=["PUT"])
def update_profile(user_id):
    """Tạo hoặc cập nhật profile của user."""
    if user_id not in users:
        return error_response("User not found", 404)

    data = request.get_json()

    profile = {
        "user_id": user_id,
        "full_name": data.get("full_name", ""),
        "bio": data.get("bio", "")
    }

    profiles[user_id] = profile

    return jsonify(profile)


# =========================================================
# SUB-RESOURCE: FOLLOWING (Collection - thuộc về User)
# ---------------------------------------------------------
# GET  /api/v1/users/:id/following            → Danh sách đang follow
# POST /api/v1/users/:id/following            → Follow user khác
# DELETE /api/v1/users/:id/following/:target   → Unfollow
# =========================================================

@app.route("/api/v1/users/<int:user_id>/following", methods=["GET"])
def get_following(user_id):
    """Lấy danh sách user đang được follow."""
    if user_id not in users:
        return error_response("User not found", 404)

    followed_ids = following.get(user_id, [])

    result = [
        users[uid]
        for uid in followed_ids
        if uid in users
    ]

    return jsonify(result)


@app.route("/api/v1/users/<int:user_id>/following", methods=["POST"])
def follow_user(user_id):
    """Follow một user khác."""
    if user_id not in users:
        return error_response("User not found", 404)

    data = request.get_json()
    target_id = data.get("user_id")

    if target_id not in users:
        return error_response("Target user not found", 404)

    if target_id == user_id:
        return error_response("Cannot follow yourself", 400)

    if user_id not in following:
        following[user_id] = []

    if target_id in following[user_id]:
        return error_response("Already following this user", 400)

    following[user_id].append(target_id)

    return jsonify({
        "user_id": user_id,
        "following_user_id": target_id
    }), 201


@app.route("/api/v1/users/<int:user_id>/following/<int:target_id>", methods=["DELETE"])
def unfollow_user(user_id, target_id):
    """Unfollow một user."""
    if user_id not in users:
        return error_response("User not found", 404)

    if target_id not in users:
        return error_response("Target user not found", 404)

    user_following = following.get(user_id, [])

    if target_id not in user_following:
        return error_response("Not following this user", 400)

    user_following.remove(target_id)

    return "", 204


# =========================================================
# RESOURCE: POSTS (Collection + Item)
# ---------------------------------------------------------
# GET    /api/v1/posts             → Lấy danh sách posts
# POST   /api/v1/posts             → Tạo post mới
# GET    /api/v1/posts/:id         → Lấy 1 post
# PUT    /api/v1/posts/:id         → Thay thế toàn bộ post
# PATCH  /api/v1/posts/:id         → Cập nhật 1 phần post
# DELETE /api/v1/posts/:id         → Xóa post
# =========================================================

@app.route("/api/v1/posts", methods=["GET"])
def get_posts():
    """Lấy danh sách tất cả posts. Hỗ trợ filter theo author_id."""
    author_id = request.args.get("author_id", type=int)

    if author_id is not None:
        result = [
            post for post in posts.values()
            if post["author_id"] == author_id
        ]
        return jsonify(result)

    return jsonify(list(posts.values()))


@app.route("/api/v1/posts", methods=["POST"])
def create_post():
    """Tạo post mới."""
    data = request.get_json()

    if not data or "title" not in data or "content" not in data or "author_id" not in data:
        return error_response("Missing required fields: title, content, author_id", 400)

    author_id = data["author_id"]

    if author_id not in users:
        return error_response("Author not found", 404)

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
    """Lấy thông tin 1 post theo ID."""
    post = posts.get(post_id)

    if not post:
        return error_response("Post not found", 404)

    return jsonify(post)


@app.route("/api/v1/posts/<int:post_id>", methods=["PUT"])
def replace_post(post_id):
    """Thay thế toàn bộ post."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    data = request.get_json()

    if not data or "title" not in data or "content" not in data or "author_id" not in data:
        return error_response("Missing required fields: title, content, author_id", 400)

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
        return error_response("Post not found", 404)

    data = request.get_json()

    if "title" in data:
        posts[post_id]["title"] = data["title"]

    if "content" in data:
        posts[post_id]["content"] = data["content"]

    return jsonify(posts[post_id])


@app.route("/api/v1/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Xóa post và các comments, tags liên quan."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    # Xóa comments thuộc post
    comment_ids_to_delete = [
        cid for cid, c in comments.items()
        if c["post_id"] == post_id
    ]
    for cid in comment_ids_to_delete:
        del comments[cid]

    # Xóa quan hệ post-tags
    post_tags.pop(post_id, None)

    del posts[post_id]

    return "", 204


# =========================================================
# SUB-RESOURCE: COMMENTS (Collection - thuộc về Post)
# ---------------------------------------------------------
# GET  /api/v1/posts/:id/comments        → Lấy comments của post
# POST /api/v1/posts/:id/comments        → Tạo comment mới
# DELETE /api/v1/posts/:pid/comments/:cid → Xóa comment
# =========================================================

@app.route("/api/v1/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    """Lấy danh sách comments của 1 post."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    result = [
        comment
        for comment in comments.values()
        if comment["post_id"] == post_id
    ]

    return jsonify(result)


@app.route("/api/v1/posts/<int:post_id>/comments", methods=["POST"])
def create_comment(post_id):
    """Tạo comment mới cho 1 post."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    data = request.get_json()

    if not data or "user_id" not in data or "content" not in data:
        return error_response("Missing required fields: user_id, content", 400)

    user_id = data["user_id"]

    if user_id not in users:
        return error_response("User not found", 404)

    new_id = get_next_id(comments)

    comment = {
        "id": new_id,
        "post_id": post_id,
        "user_id": user_id,
        "content": data["content"]
    }

    comments[new_id] = comment

    return jsonify(comment), 201


@app.route("/api/v1/posts/<int:post_id>/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(post_id, comment_id):
    """Xóa comment của 1 post."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    comment = comments.get(comment_id)

    if not comment or comment["post_id"] != post_id:
        return error_response("Comment not found", 404)

    del comments[comment_id]

    return "", 204


# =========================================================
# RESOURCE: TAGS (Collection + Item)
# ---------------------------------------------------------
# GET  /api/v1/tags       → Lấy danh sách tags
# POST /api/v1/tags       → Tạo tag mới
# =========================================================

@app.route("/api/v1/tags", methods=["GET"])
def get_tags():
    """Lấy danh sách tất cả tags."""
    return jsonify(list(tags.values()))


@app.route("/api/v1/tags", methods=["POST"])
def create_tag():
    """Tạo tag mới."""
    data = request.get_json()

    if not data or "name" not in data:
        return error_response("Missing required field: name", 400)

    new_id = get_next_id(tags)

    tag = {
        "id": new_id,
        "name": data["name"]
    }

    tags[new_id] = tag

    return jsonify(tag), 201


# =========================================================
# SUB-RESOURCE: POST-TAGS (Quan hệ nhiều-nhiều)
# ---------------------------------------------------------
# GET    /api/v1/posts/:id/tags            → Lấy tags của post
# POST   /api/v1/posts/:id/tags            → Gắn tag vào post
# DELETE /api/v1/posts/:pid/tags/:tid      → Gỡ tag khỏi post
# =========================================================

@app.route("/api/v1/posts/<int:post_id>/tags", methods=["GET"])
def get_post_tags(post_id):
    """Lấy danh sách tags của 1 post."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    tag_ids = post_tags.get(post_id, [])

    result = [
        tags[tag_id]
        for tag_id in tag_ids
        if tag_id in tags
    ]

    return jsonify(result)


@app.route("/api/v1/posts/<int:post_id>/tags", methods=["POST"])
def add_post_tag(post_id):
    """Gắn tag vào post."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    data = request.get_json()

    if not data or "tag_id" not in data:
        return error_response("Missing required field: tag_id", 400)

    tag_id = data["tag_id"]

    if tag_id not in tags:
        return error_response("Tag not found", 404)

    if post_id not in post_tags:
        post_tags[post_id] = []

    if tag_id in post_tags[post_id]:
        return error_response("Tag already added to this post", 400)

    post_tags[post_id].append(tag_id)

    return jsonify(tags[tag_id]), 201


@app.route("/api/v1/posts/<int:post_id>/tags/<int:tag_id>", methods=["DELETE"])
def remove_post_tag(post_id, tag_id):
    """Gỡ tag khỏi post."""
    if post_id not in posts:
        return error_response("Post not found", 404)

    if tag_id not in tags:
        return error_response("Tag not found", 404)

    tag_list = post_tags.get(post_id, [])

    if tag_id not in tag_list:
        return error_response("Tag not associated with this post", 400)

    tag_list.remove(tag_id)

    return "", 204


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
