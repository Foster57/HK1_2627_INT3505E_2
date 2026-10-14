import base64
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional
from flask import request

from ..handlers.exception import ApiProblem
from ..repositories import tasks_repo

SUPPORTED_COLUMNS = {"id", "title", "status", "priority", "dueDate", "assignedID"}
ALLOWED_STATUSES = {"todo", "in_progress", "done", "cancelled"}
ALLOWED_PRIORITIES = {"low", "medium", "high", "urgent"}


@dataclass
class PaginationArgs:
    limit: int = 10
    sort_field: str = "id"
    descending: bool = False
    filters: list[str] = field(default_factory=list)
    params: list[Any] = field(default_factory=list)


def _parse_limit() -> int:
    raw = request.args.get("limit", "10")
    try:
        val = int(raw)
    except (ValueError, TypeError):
        raise ApiProblem(
            status=400,
            title="Invalid Parameter",
            detail="Tham số 'limit' phải là một số nguyên dương.",
            type_uri="https://httpstatuses.com/400",
        )
    if not (1 <= val <= 100):
        raise ApiProblem(
            status=400,
            title="Out of Range",
            detail="Giá trị 'limit' phải nằm trong khoảng từ 1 đến 100.",
            type_uri="https://httpstatuses.com/400",
        )
    return val


def _parse_sort() -> tuple[str, bool]:
    sort_query = request.args.get("sort", "id")
    is_desc = sort_query.startswith("-")
    field_name = sort_query[1:] if is_desc else sort_query

    if field_name not in SUPPORTED_COLUMNS:
        raise ApiProblem(
            status=400,
            title="Invalid Sort Field",
            detail=f"Trường sắp xếp '{field_name}' không hợp lệ. Các trường hỗ trợ: {', '.join(sorted(SUPPORTED_COLUMNS))}",
            type_uri="https://httpstatuses.com/400",
        )
    return field_name, is_desc


def _parse_filter_conditions() -> tuple[list[str], list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []

    status_filter = request.args.get("status")
    if status_filter:
        if status_filter not in ALLOWED_STATUSES:
            raise ApiProblem(
                status=400,
                title="Invalid Status Filter",
                detail=f"Trạng thái '{status_filter}' không hợp lệ. Giá trị cho phép: {', '.join(sorted(ALLOWED_STATUSES))}",
                type_uri="https://httpstatuses.com/400",
            )
        clauses.append("status = ?")
        params.append(status_filter)

    priority_filter = request.args.get("priority")
    if priority_filter:
        if priority_filter not in ALLOWED_PRIORITIES:
            raise ApiProblem(
                status=400,
                title="Invalid Priority Filter",
                detail=f"Độ ưu tiên '{priority_filter}' không hợp lệ. Giá trị cho phép: {', '.join(sorted(ALLOWED_PRIORITIES))}",
                type_uri="https://httpstatuses.com/400",
            )
        clauses.append("priority = ?")
        params.append(priority_filter)

    assigned_id_raw = request.args.get("assignedID")
    if assigned_id_raw:
        try:
            assigned_id = int(assigned_id_raw)
        except (ValueError, TypeError):
            raise ApiProblem(
                status=400,
                title="Invalid Assigned ID",
                detail="Tham số 'assignedID' phải là một số nguyên dương.",
                type_uri="https://httpstatuses.com/400",
            )
        clauses.append("assignedID = ?")
        params.append(assigned_id)

    return clauses, params


def parse_pagination_context() -> PaginationArgs:
    limit = _parse_limit()
    sort_field, is_desc = _parse_sort()
    filters, params = _parse_filter_conditions()

    return PaginationArgs(
        limit=limit,
        sort_field=sort_field,
        descending=is_desc,
        filters=filters,
        params=params,
    )


# ==============================================================================
# Xử lý Cursor (Keyset Pagination)
# ==============================================================================

def encode_cursor(sort_field: str, sort_value: Any, task_id: int) -> str:
    payload = {"sort": sort_field, "val": str(sort_value), "id": task_id}
    dumped = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(dumped).decode("ascii").rstrip("=")


def decode_cursor(token: str) -> dict[str, Any]:
    try:
        padded = token + "=" * (-len(token) % 4)
        raw_bytes = base64.urlsafe_b64decode(padded.encode("ascii"))
        payload = json.loads(raw_bytes.decode("utf-8"))

        if (
            not isinstance(payload, dict)
            or payload.get("sort") not in SUPPORTED_COLUMNS
            or "val" not in payload
            or not isinstance(payload.get("id"), int)
        ):
            raise ValueError("Malformed cursor payload")
        return payload
    except Exception:
        raise ApiProblem(
            status=400,
            title="Malformed Cursor",
            detail="Chuỗi con trỏ (cursor) không hợp lệ hoặc đã bị lỗi định dạng.",
            type_uri="https://httpstatuses.com/400",
        )


def build_cursor_condition(sort_field: str, descending: bool, cursor_data: dict[str, Any]) -> tuple[str, list[Any]]:
    op = "<" if descending else ">"
    clause = f"({sort_field} {op} ? OR ({sort_field} = ? AND id {op} ?))"
    params = [cursor_data["val"], cursor_data["val"], cursor_data["id"]]
    return clause, params


# ==============================================================================
# Helper Serialization
# ==============================================================================

def serialize_task_row(row: Any) -> dict[str, Any]:
    item = dict(row)
    if "dueDate" in item and isinstance(item["dueDate"], str):
        try:
            item["dueDate"] = date.fromisoformat(item["dueDate"])
        except ValueError:
            pass
    return item


# ==============================================================================
# Business Service Functions
# ==============================================================================

def list_tasks_service(paginate: PaginationArgs) -> tuple[list[dict[str, Any]], Optional[str], bool]:
    cursor_token = request.args.get("cursor")
    if cursor_token:
        cursor_data = decode_cursor(cursor_token)
        if cursor_data["sort"] != paginate.sort_field:
            raise ApiProblem(
                status=400,
                title="Cursor Mismatch",
                detail="Con trỏ cursor không khớp với tiêu chí sắp xếp đang yêu cầu.",
                type_uri="https://httpstatuses.com/400",
            )
        c_clause, c_params = build_cursor_condition(
            paginate.sort_field, paginate.descending, cursor_data
        )
        paginate.filters.append(c_clause)
        paginate.params.extend(c_params)

    records = tasks_repo.fetch_tasks(
        paginate.filters,
        paginate.params,
        paginate.sort_field,
        paginate.descending,
        paginate.limit,
    )

    has_more = len(records) > paginate.limit
    page_records = records[: paginate.limit]
    data = [serialize_task_row(r) for r in page_records]

    next_cursor = None
    if has_more and page_records:
        last_item = page_records[-1]
        next_cursor = encode_cursor(
            paginate.sort_field,
            last_item[paginate.sort_field],
            last_item["id"],
        )

    return data, next_cursor, has_more


def get_task_service(task_id: int) -> dict[str, Any]:
    row = tasks_repo.find_by_id(task_id)
    if row is None:
        raise ApiProblem(
            status=404,
            title="Task Not Found",
            detail=f"Không tìm thấy công việc với ID = {task_id}.",
            type_uri="https://httpstatuses.com/404",
            instance=f"/tasks/{task_id}",
        )
    return serialize_task_row(row)


def create_task_service(payload: dict[str, Any]) -> dict[str, Any]:
    # Ép kiểu date sang chuỗi YYYY-MM-DD lưu vào SQLite
    clean_data = dict(payload)
    if isinstance(clean_data.get("dueDate"), date):
        clean_data["dueDate"] = clean_data["dueDate"].isoformat()

    new_id = tasks_repo.insert_task(clean_data)
    return get_task_service(new_id)


def update_task_service(task_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    if tasks_repo.find_by_id(task_id) is None:
        raise ApiProblem(
            status=404,
            title="Task Not Found",
            detail=f"Không thể cập nhật: không tìm thấy công việc với ID = {task_id}.",
            type_uri="https://httpstatuses.com/404",
            instance=f"/tasks/{task_id}",
        )

    clean_data = dict(payload)
    if not clean_data:
        raise ApiProblem(
            status=400,
            title="Empty Payload",
            detail="Dữ liệu cập nhật PATCH không được rỗng.",
            type_uri="https://httpstatuses.com/400",
        )

    if isinstance(clean_data.get("dueDate"), date):
        clean_data["dueDate"] = clean_data["dueDate"].isoformat()

    tasks_repo.update_task(task_id, clean_data)
    return get_task_service(task_id)


def delete_task_service(task_id: int) -> None:
    affected = tasks_repo.delete_task(task_id)
    if affected == 0:
        raise ApiProblem(
            status=404,
            title="Task Not Found",
            detail=f"Không thể xóa: công việc với ID = {task_id} không tồn tại.",
            type_uri="https://httpstatuses.com/404",
            instance=f"/tasks/{task_id}",
        )