-- ==============================================================================
-- Schema: Internal Task Management System
-- Database: SQLite 3
-- ==============================================================================

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL CHECK(length(trim(title)) > 0),
    status      TEXT    NOT NULL CHECK(status IN ('todo', 'in_progress', 'done', 'cancelled')),
    priority    TEXT    NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    dueDate     TEXT    NOT NULL,  -- Định dạng chuẩn ISO-8601: YYYY-MM-DD
    assignedID  INTEGER NOT NULL CHECK(assignedID > 0)
);

-- Chỉ mục hỗ trợ tìm kiếm, lọc và phân trang (Keyset / Cursor pagination)
CREATE INDEX IF NOT EXISTS idx_tasks_status     ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority   ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_assignedID ON tasks(assignedID);
CREATE INDEX IF NOT EXISTS idx_tasks_dueDate    ON tasks(dueDate);
CREATE INDEX IF NOT EXISTS idx_tasks_id_desc    ON tasks(id DESC);

-- ==============================================================================
-- Dữ liệu mẫu khởi tạo (Seed Data)
-- ==============================================================================

INSERT INTO tasks (title, status, priority, dueDate, assignedID) VALUES
    ('Thiết kế kiến trúc hệ thống và luồng dữ liệu microservices', 'done',        'high',   '2026-03-01', 101),
    ('Viết đặc tả OpenAPI 3.0 cho Petstore API',                   'done',        'medium', '2026-03-05', 102),
    ('Cấu hình Flask-Smorest và Swagger UI cho Tasks API',         'in_progress', 'urgent', '2026-03-10', 101),
    ('Xây dựng middleware chuẩn hóa mã lỗi RFC 7807',              'in_progress', 'high',   '2026-03-12', 103),
    ('Triển khai phân trang dạng Keyset Cursor cho bảng tasks',     'in_progress', 'high',   '2026-03-15', 104),
    ('Thiết lập kết nối cơ sở dữ liệu SQLite và Transaction',      'done',        'medium', '2026-03-08', 102),
    ('Tối ưu hóa truy vấn SQL với Composite Indexes',             'todo',        'medium', '2026-03-18', 104),
    ('Tích hợp kiểm thử tự động Pytest cho các endpoint CRUD',     'todo',        'high',   '2026-03-20', 103),
    ('Kiểm thử tải hiệu năng API với k6 và Locust',                'todo',        'low',    '2026-03-25', 105),
    ('Đóng gói container Dockerfile cho dịch vụ Tasks',            'todo',        'medium', '2026-03-28', 101),
    ('Xây dựng luồng CI/CD với GitHub Actions',                   'todo',        'low',    '2026-03-30', 102),
    ('Đánh giá lỗ hổng bảo mật và phân quyền truy cập RBAC',       'cancelled',   'urgent', '2026-03-02', 105),
    ('Tạo tài liệu hướng dẫn triển khai và tích hợp cho FE',       'todo',        'low',    '2026-04-02', 103),
    ('Giám sát hệ thống với Prometheus và Grafana metrics',        'todo',        'medium', '2026-04-05', 104),
    ('Họp tổng kết sprint và review mã nguồn tuần 4',              'done',        'low',    '2026-03-07', 101);