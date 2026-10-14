from marshmallow import Schema, fields, validate, EXCLUDE

VALID_STATUSES = ["todo", "in_progress", "done", "cancelled"]
VALID_PRIORITIES = ["low", "medium", "high", "urgent"]


class TaskSchema(Schema):
    """Schema biểu diễn đầy đủ một bản ghi Task trả về cho client."""

    id = fields.Int(
        dump_only=True,
        metadata={
            "description": "Mã định danh duy nhất của task (khóa chính tự tăng)",
            "example": 1,
        },
    )
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={
            "description": "Tiêu đề tóm tắt nội dung công việc",
            "example": "Triển khai xác thực JWT cho API Gateway",
        },
    )
    status = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_STATUSES),
        metadata={
            "description": "Trạng thái thực hiện (todo, in_progress, done, cancelled)",
            "example": "in_progress",
        },
    )
    priority = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_PRIORITIES),
        metadata={
            "description": "Mức độ ưu tiên công việc (low, medium, high, urgent)",
            "example": "high",
        },
    )
    dueDate = fields.Date(
        required=True,
        metadata={
            "description": "Hạn hoàn thành công việc theo chuẩn ISO 8601 (YYYY-MM-DD)",
            "example": "2026-03-31",
        },
    )
    assignedID = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        metadata={
            "description": "Mã ID nhân viên chịu trách nhiệm xử lý task",
            "example": 101,
        },
    )


class TaskInputSchema(Schema):
    """Schema dữ liệu đầu vào khi tạo mới một Task (POST /tasks)."""

    class Meta:
        unknown = EXCLUDE

    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={
            "description": "Tiêu đề bắt buộc của task mới",
            "example": "Xây dựng tài liệu OpenAPI cho module Đơn hàng",
        },
    )
    status = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_STATUSES),
        metadata={
            "description": "Trạng thái ban đầu của task",
            "example": "todo",
        },
    )
    priority = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_PRIORITIES),
        metadata={
            "description": "Độ ưu tiên công việc",
            "example": "medium",
        },
    )
    dueDate = fields.Date(
        required=True,
        metadata={
            "description": "Hạn chót hoàn thành (YYYY-MM-DD)",
            "example": "2026-04-15",
        },
    )
    assignedID = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        metadata={
            "description": "ID người được phân công",
            "example": 102,
        },
    )


class TaskUpdateSchema(Schema):
    """Schema cập nhật một phần dữ liệu Task (PATCH /tasks/{id}). Các trường đều là tùy chọn."""

    class Meta:
        unknown = EXCLUDE

    title = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=255),
        metadata={"description": "Tiêu đề cập nhật"},
    )
    status = fields.Str(
        required=False,
        validate=validate.OneOf(VALID_STATUSES),
        metadata={"description": "Trạng thái cập nhật"},
    )
    priority = fields.Str(
        required=False,
        validate=validate.OneOf(VALID_PRIORITIES),
        metadata={"description": "Mức ưu tiên cập nhật"},
    )
    dueDate = fields.Date(
        required=False,
        metadata={"description": "Hạn hoàn thành mới (YYYY-MM-DD)"},
    )
    assignedID = fields.Int(
        required=False,
        validate=validate.Range(min=1),
        metadata={"description": "ID người được chuyển giao công việc"},
    )


class TaskListSchema(Schema):
    """Schema phản hồi danh sách task có kèm con trỏ phân trang (Cursor Pagination)."""

    data = fields.List(
        fields.Nested(TaskSchema),
        metadata={"description": "Danh sách các công việc trong trang hiện tại"},
    )
    next_cursor = fields.Str(
        allow_none=True,
        metadata={
            "description": "Con trỏ opaque Base64 dùng để lấy trang tiếp theo (None nếu là trang cuối)",
            "example": "eyJzb3J0IjoiaWQiLCJ2YWx1ZSI6MTAsImlkIjoxMH0",
        },
    )
    has_more = fields.Bool(
        metadata={
            "description": "Đánh dấu còn dữ liệu ở các trang sau hay không",
            "example": True,
        },
    )