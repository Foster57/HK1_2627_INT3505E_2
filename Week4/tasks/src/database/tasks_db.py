import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DATABASE_DIR = Path(__file__).resolve().parent
DB_FILE_PATH = DATABASE_DIR / "tasks.db"
SCHEMA_FILE_PATH = DATABASE_DIR / "schemas.sql"


def get_db() -> sqlite3.Connection:
    """Khởi tạo kết nối SQLite với cấu hình row_factory và foreign keys."""
    conn = sqlite3.connect(str(DB_FILE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(force: bool = False) -> None:
    """
    Khởi tạo cấu trúc bảng và nạp dữ liệu mẫu ban đầu từ schemas.sql.
    Nếu force=True hoặc cơ sở dữ liệu chưa tồn tại, thực thi toàn bộ script.
    """
    if not force and DB_FILE_PATH.exists() and DB_FILE_PATH.stat().st_size > 0:
        return

    logger.info("Đang khởi tạo cơ sở dữ liệu SQLite tại: %s", DB_FILE_PATH)
    if not SCHEMA_FILE_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file schema tại {SCHEMA_FILE_PATH}")

    sql_script = SCHEMA_FILE_PATH.read_text(encoding="utf-8")
    with get_db() as conn:
        conn.executescript(sql_script)
        conn.commit()
    logger.info("Khởi tạo cơ sở dữ liệu thành công với các bảng và dữ liệu mẫu.")