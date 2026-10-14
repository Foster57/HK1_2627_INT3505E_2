from marshmallow import Schema, fields, INCLUDE


class ErrorDetailSchema(Schema):
    """Chi tiết từng trường lỗi (dành cho validation errors)."""
    field = fields.Str(metadata={"description": "Tên trường bị lỗi"})
    message = fields.Str(metadata={"description": "Nội dung thông báo lỗi chi tiết"})


class ProblemDetailsSchema(Schema):
    """
    Đặc tả phản hồi lỗi chuẩn RFC 7807 (Problem Details for HTTP APIs).
    Content-Type: application/problem+json
    """

    class Meta:
        unknown = INCLUDE

    type = fields.Str(
        required=True,
        metadata={
            "description": "URI định danh loại lỗi",
            "example": "https://httpstatuses.com/404",
        },
    )
    title = fields.Str(
        required=True,
        metadata={
            "description": "Tiêu đề ngắn gọn mô tả loại lỗi",
            "example": "Not Found",
        },
    )
    status = fields.Int(
        required=True,
        metadata={
            "description": "Mã trạng thái HTTP tương ứng",
            "example": 404,
        },
    )
    detail = fields.Str(
        required=False,
        metadata={
            "description": "Mô tả cụ thể về sự cố xảy ra cho request này",
            "example": "Không tìm thấy task với ID được cung cấp.",
        },
    )
    instance = fields.Str(
        required=False,
        metadata={
            "description": "URI endpoint đã kích hoạt lỗi",
            "example": "/tasks/99",
        },
    )
    trace_id = fields.Str(
        required=False,
        metadata={
            "description": "Mã định danh duy nhất của request phục vụ tra cứu log",
            "example": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        },
    )