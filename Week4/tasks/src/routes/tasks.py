from flask.views import MethodView
from flask_smorest import Blueprint

from ..schemas.tasks import (
    TaskSchema,
    TaskInputSchema,
    TaskUpdateSchema,
    TaskListSchema,
)
from ..schemas.exception import ProblemDetailsSchema
from ..services.tasks_service import (
    parse_pagination_context,
    list_tasks_service,
    get_task_service,
    create_task_service,
    update_task_service,
    delete_task_service,
)

blp = Blueprint(
    "tasks",
    __name__,
    url_prefix="/tasks",
    description="Tập hợp các API quản lý công việc (Tasks Management)",
)


@blp.route("")
@blp.route("/")
class TaskListEndpoint(MethodView):

    @blp.response(200, TaskListSchema, description="Lấy danh sách công việc thành công kèm con trỏ phân trang")
    @blp.alt_response(400, schema=ProblemDetailsSchema, description="Tham số truy vấn lọc/phân trang không hợp lệ")
    @blp.alt_response(500, schema=ProblemDetailsSchema, description="Lỗi xử lý nội bộ phía máy chủ")
    def get(self):
        """
        Lấy danh sách công việc (Hỗ trợ lọc & Keyset Cursor Pagination)
        ---
        Cho phép lọc theo status, priority, assignedID và sắp xếp linh hoạt theo các trường.
        """
        pagination_args = parse_pagination_context()
        items, next_cursor, has_more = list_tasks_service(pagination_args)
        return {
            "data": items,
            "next_cursor": next_cursor,
            "has_more": has_more,
        }

    @blp.arguments(TaskInputSchema, description="Dữ liệu công việc cần khởi tạo")
    @blp.response(201, TaskSchema, description="Tạo mới công việc thành công")
    @blp.alt_response(400, schema=ProblemDetailsSchema, description="Dữ liệu payload gửi lên vi phạm quy tắc validation")
    @blp.alt_response(500, schema=ProblemDetailsSchema, description="Lỗi máy chủ khi ghi dữ liệu")
    def post(self, payload):
        """
        Tạo mới một công việc
        ---
        Yêu cầu cung cấp đầy đủ: title, status, priority, dueDate (YYYY-MM-DD), assignedID.
        """
        return create_task_service(payload)


@blp.route("/<int:task_id>")
class TaskDetailEndpoint(MethodView):

    @blp.response(200, TaskSchema, description="Trả về thông tin chi tiết của công việc")
    @blp.alt_response(404, schema=ProblemDetailsSchema, description="Không tìm thấy ID công việc yêu cầu")
    @blp.alt_response(500, schema=ProblemDetailsSchema, description="Lỗi máy chủ khi đọc cơ sở dữ liệu")
    def get(self, task_id: int):
        """
        Xem chi tiết công việc theo ID
        ---
        Truy vấn thông tin của một bản ghi công việc dựa trên khóa chính id.
        """
        return get_task_service(task_id)

    @blp.arguments(TaskUpdateSchema, description="Các trường thông tin cần cập nhật một phần")
    @blp.response(200, TaskSchema, description="Cập nhật thành công và trả về dữ liệu mới nhất")
    @blp.alt_response(400, schema=ProblemDetailsSchema, description="Payload rỗng hoặc giá trị trường không hợp lệ")
    @blp.alt_response(404, schema=ProblemDetailsSchema, description="Không tìm thấy ID công việc để cập nhật")
    @blp.alt_response(500, schema=ProblemDetailsSchema, description="Lỗi máy chủ khi cập nhật dữ liệu")
    def patch(self, payload, task_id: int):
        """
        Cập nhật một phần thông tin công việc (Partial Update)
        ---
        Chỉ cập nhật những trường được gửi lên trong request body.
        """
        return update_task_service(task_id, payload)

    @blp.response(204, description="Xóa công việc thành công (Không trả về nội dung)")
    @blp.alt_response(404, schema=ProblemDetailsSchema, description="Không tìm thấy ID công việc để xóa")
    @blp.alt_response(500, schema=ProblemDetailsSchema, description="Lỗi máy chủ khi xóa bản ghi")
    def delete(self, task_id: int):
        """
        Xóa một công việc theo ID
        ---
        Xóa vĩnh viễn bản ghi khỏi cơ sở dữ liệu nếu tồn tại.
        """
        delete_task_service(task_id)
        return "", 204