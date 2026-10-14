import sqlite3
from typing import Any, Optional
from ..database.tasks_db import get_db

TASK_COLUMNS = ("id", "title", "status", "priority", "dueDate", "assignedID")
COLUMN_SELECTION = ", ".join(TASK_COLUMNS)


def fetch_tasks(
    filter_clauses: list[str],
    filter_params: list[Any],
    sort_column: str,
    descending: bool,
    limit: int,
) -> list[sqlite3.Row]:
    """
    Truy vấn danh sách tasks có điều kiện lọc, sắp xếp và giới hạn.
    Lấy thêm 1 bản ghi (limit + 1) để xác định xem còn trang tiếp theo hay không.
    """
    where_sql = ""
    if filter_clauses:
        where_sql = "WHERE " + " AND ".join(filter_clauses)

    sort_direction = "DESC" if descending else "ASC"
    sql = f"""
        SELECT {COLUMN_SELECTION}
        FROM tasks
        {where_sql}
        ORDER BY {sort_column} {sort_direction}, id {sort_direction}
        LIMIT ?
    """

    conn = get_db()
    try:
        return conn.execute(sql, filter_params + [limit + 1]).fetchall()
    finally:
        conn.close()


def find_by_id(task_id: int) -> Optional[sqlite3.Row]:
    """Tìm một task theo khóa chính id."""
    conn = get_db()
    try:
        query = f"SELECT {COLUMN_SELECTION} FROM tasks WHERE id = ?"
        return conn.execute(query, (task_id,)).fetchone()
    finally:
        conn.close()


def insert_task(payload: dict[str, Any]) -> int:
    """Tạo mới một bản ghi task và trả về ID vừa sinh."""
    conn = get_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO tasks (title, status, priority, dueDate, assignedID)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload["title"],
                payload["status"],
                payload["priority"],
                payload["dueDate"],
                payload["assignedID"],
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def update_task(task_id: int, updates: dict[str, Any]) -> int:
    """Cập nhật các trường được chỉ định của task. Trả về số dòng bị ảnh hưởng."""
    if not updates:
        return 0

    clauses = [f"{col} = ?" for col in updates.keys()]
    values = list(updates.values()) + [task_id]
    sql = f"UPDATE tasks SET {', '.join(clauses)} WHERE id = ?"

    conn = get_db()
    try:
        cursor = conn.execute(sql, values)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_task(task_id: int) -> int:
    """Xóa bản ghi task theo ID. Trả về số dòng bị ảnh hưởng."""
    conn = get_db()
    try:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()