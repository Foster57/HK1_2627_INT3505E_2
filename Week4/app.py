from flask import Flask, jsonify, request, make_response, redirect
from functools import wraps
from pathlib import Path
import uuid
import yaml


app = Flask(__name__)


# ==========================================================
# Demo Bearer Token (ghi rõ trong README)
# Đây là token demo dùng cho mục đích kiểm thử bài tập.
# Trong production, cần dùng JWT thật (ví dụ: PyJWT).
# ==========================================================

DEMO_TOKEN = "demo-bearer-token-week4"


# ==========================================================
# In-memory database
# ==========================================================

TASKS = {
    "3fa85f64-5717-4562-b3fc-2c963f66afa6": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "title": "Thiết kế API specification cho Tasks",
        "status": "open",
        "priority": "high",
        "dueDate": "2026-10-20",
        "assigneeId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    "7c9e6679-7425-40de-944b-e07fc1f90ae7": {
        "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
        "title": "Cấu hình Swagger UI và tài liệu OpenAPI",
        "status": "done",
        "priority": "normal",
        "dueDate": "2026-10-15",
        "assigneeId": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    },
    "aabbccdd-1122-3344-5566-778899aabbcc": {
        "id": "aabbccdd-1122-3344-5566-778899aabbcc",
        "title": "Viết README bằng tiếng Việt",
        "status": "open",
        "priority": "low",
        "dueDate": "2026-10-25",
        "assigneeId": None
    }
}


# ==========================================================
# Helper: RFC 7807 Problem Details error response
# ==========================================================

def problem(status, title, detail):
    response = jsonify({
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path
    })

    response.status_code = status
    response.headers["Content-Type"] = "application/problem+json"

    return response


def find_task(task_id):
    return TASKS.get(task_id)


# ==========================================================
# Helper: Bearer Token authentication decorator
# ==========================================================

def require_auth(f):
    """
    Decorator kiểm tra Bearer Token trong header Authorization.
    Header phải có dạng: Authorization: Bearer <token>
    Token demo: demo-bearer-token-week4
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return problem(
                401,
                "Unauthorized",
                "Missing or invalid Authorization header. "
                "Use: Authorization: Bearer <token>"
            )

        token = auth_header[len("Bearer "):]

        if token != DEMO_TOKEN:
            return problem(
                401,
                "Unauthorized",
                "Invalid Bearer token."
            )

        return f(*args, **kwargs)

    return decorated


# ==========================================================
# GET /v1/tasks
# ==========================================================

@app.get("/v1/tasks")
@app.get("/tasks")
@require_auth
def list_tasks():

    tasks = list(TASKS.values())

    # status filter
    status = request.args.get("status")

    if status:
        if status not in {"open", "done"}:
            return problem(
                422,
                "Validation error",
                "status must be open or done"
            )

        tasks = [
            task
            for task in tasks
            if task["status"] == status
        ]

    # limit
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return problem(
            422,
            "Validation error",
            "limit must be an integer"
        )

    if limit < 1 or limit > 100:
        return problem(
            422,
            "Validation error",
            "limit must be between 1 and 100"
        )

    tasks = tasks[:limit]

    return jsonify({
        "data": tasks,
        "total": len(tasks)
    }), 200


# ==========================================================
# POST /v1/tasks
# ==========================================================

@app.post("/v1/tasks")
@app.post("/tasks")
@require_auth
def create_task():

    if not request.is_json:
        return problem(
            415,
            "Unsupported Media Type",
            "Content-Type must be application/json"
        )

    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()

    if not title:
        return problem(
            422,
            "Validation error",
            "title is required"
        )

    status = data.get("status", "open")
    priority = data.get("priority", "normal")

    if status not in {"open", "done"}:
        return problem(
            422,
            "Validation error",
            "status must be open or done"
        )

    if priority not in {"low", "normal", "high"}:
        return problem(
            422,
            "Validation error",
            "priority must be low, normal or high"
        )

    task_id = str(uuid.uuid4())

    task = {
        "id": task_id,
        "title": title,
        "status": status,
        "priority": priority,
        "dueDate": data.get("dueDate"),
        "assigneeId": data.get("assigneeId")
    }

    TASKS[task_id] = task

    response = make_response(jsonify(task), 201)

    response.headers["Location"] = (
        f"/v1/tasks/{task_id}"
    )

    return response


# ==========================================================
# GET /v1/tasks/{taskId}
# ==========================================================

@app.get("/v1/tasks/<task_id>")
@app.get("/tasks/<task_id>")
@require_auth
def get_task(task_id):

    task = find_task(task_id)

    if task is None:
        return problem(
            404,
            "Task not found",
            f"Task {task_id} does not exist"
        )

    return jsonify(task), 200


# ==========================================================
# PATCH /v1/tasks/{taskId}
# ==========================================================

@app.patch("/v1/tasks/<task_id>")
@app.patch("/tasks/<task_id>")
@require_auth
def patch_task(task_id):

    task = find_task(task_id)

    if task is None:
        return problem(
            404,
            "Task not found",
            f"Task {task_id} does not exist"
        )

    if not request.is_json:
        return problem(
            415,
            "Unsupported Media Type",
            "Content-Type must be application/json"
        )

    data = request.get_json(silent=True) or {}

    # Không cho phép thay đổi id
    if "id" in data:
        return problem(
            422,
            "Validation error",
            "Field 'id' cannot be modified"
        )

    if "title" in data:

        title = str(data["title"]).strip()

        if not title:
            return problem(
                422,
                "Validation error",
                "title must not be empty"
            )

        task["title"] = title

    if "status" in data:

        if data["status"] not in {"open", "done"}:
            return problem(
                422,
                "Validation error",
                "status must be open or done"
            )

        task["status"] = data["status"]

    if "priority" in data:

        if data["priority"] not in {
            "low",
            "normal",
            "high"
        }:
            return problem(
                422,
                "Validation error",
                "priority must be low, normal or high"
            )

        task["priority"] = data["priority"]

    if "dueDate" in data:
        task["dueDate"] = data["dueDate"]

    if "assigneeId" in data:
        task["assigneeId"] = data["assigneeId"]

    return jsonify(task), 200


# ==========================================================
# DELETE /v1/tasks/{taskId}
# ==========================================================

@app.delete("/v1/tasks/<task_id>")
@app.delete("/tasks/<task_id>")
@require_auth
def delete_task(task_id):

    if task_id not in TASKS:
        return problem(
            404,
            "Task not found",
            f"Task {task_id} does not exist"
        )

    del TASKS[task_id]

    return "", 204


# ==========================================================
# GET /openapi.json — phục vụ Swagger UI
# ==========================================================

@app.get("/openapi.json")
def openapi_json():

    yaml_path = Path(__file__).parent / "tasks-api.yaml"
    if not yaml_path.exists():
        yaml_path = Path(__file__).parent / "openapi.yaml"

    with yaml_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        spec = yaml.safe_load(file)

    return jsonify(spec)


# ==========================================================
# GET /docs — Swagger UI
# ==========================================================

@app.get("/docs")
def swagger_docs():

    return """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8" />
    <title>Tasks API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: "/openapi.json",
            dom_id: "#swagger-ui",
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            deepLinking: true
        });
    </script>
</body>
</html>"""


# ==========================================================
# GET / — Chuyển hướng về trang tài liệu Swagger UI
# ==========================================================

@app.get("/")
def index():
    return redirect("/docs")


if __name__ == "__main__":
    app.run(debug=True)
