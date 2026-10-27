# SecurityAudit.md

Phạm vi: `POST /auth/login`, `POST /auth/refresh`, `GET /posts/{id}` (xem `openapi.yaml`).

## Các điểm có thể lộ

| # | Điểm có thể lộ | Endpoint | Mức | Cách giảm thiểu (đã phản ánh trong spec) |
|---|---|---|---|---|
| 1 | **User enumeration**: thông báo/thời gian phản hồi khác nhau giữa "email không tồn tại" và "sai mật khẩu" | login | Cao | Luôn trả `401 INVALID_CREDENTIALS` chung; so sánh hash cả khi email không tồn tại để đồng đều thời gian |
| 2 | **Brute force / credential stuffing**: không giới hạn số lần thử | login | Cao | Rate limit theo IP + theo tài khoản (`429` + `Retry-After`), khóa tạm/CAPTCHA sau N lần sai, hash mật khẩu bằng argon2id/bcrypt |
| 3 | **Đánh cắp & replay refresh token** (sống lâu, dùng được nhiều lần) | refresh | Cao | Rotation: dùng một lần; phát hiện reuse → thu hồi cả chuỗi (`REFRESH_TOKEN_REUSED`); lưu server dưới dạng hash; TTL hợp lý, gắn với thiết bị |
| 4 | **Token/mật khẩu lộ qua log, URL, cache** | cả 3 | Cao | Không log body login/refresh; không đưa token vào query string; response token có `Cache-Control: no-store`; mask header `Authorization` trong log |
| 5 | **BOLA/IDOR**: đổi `{id}` để đọc bài riêng tư của người khác | posts/{id} | Cao | Kiểm tra quyền trên từng object (visibility, quan hệ bạn bè, chặn) ở server, không chỉ kiểm tra scope |
| 6 | **Lộ sự tồn tại tài nguyên** qua khác biệt 403 vs 404; ID tuần tự dễ dò | posts/{id} | Trung bình | Trả `404` cho bài không có quyền xem; dùng UUID thay vì số tự tăng |
| 7 | **Excessive data exposure**: schema Post trả thừa (email tác giả, IP, cờ kiểm duyệt, trường nội bộ) | posts/{id} | Trung bình | Dùng DTO/whitelist trường; chỉ trả `author.id/display_name/avatar_url`; lọc nội dung bài đã xóa |
| 8 | **Cấu hình JWT sai**: `alg=none`/đổi thuật toán, thiếu `iss`/`aud`/`exp`, TTL dài, tin scope từ client | posts/{id}, refresh | Cao | Cố định thuật toán, kiểm chữ ký + `iss`/`aud`/`exp`; access token ngắn (~15 phút); scope lấy từ server/claim đã ký, kiểm tra mỗi request |
| 9 | **Thông báo lỗi chi tiết** (stack trace, SQL error, phiên bản framework) | cả 3 | Trung bình | `500` chung kèm `request_id`; chi tiết chỉ ghi log nội bộ; dùng `code` ổn định |
| 10 | **Thiếu TLS/HSTS, CORS quá rộng** → token bị chặn hoặc bị trang lạ gọi API | cả 3 | Cao | Chỉ HTTPS + HSTS; CORS whitelist origin; không dùng `*` với credentials |

## Ma trận scope / lỗi (tóm tắt)

| Endpoint | Scope | Status trả về |
|---|---|---|
| `POST /auth/login` | không (public) | 200, 400, 401, 403, 415, 429, 500 |
| `POST /auth/refresh` | không (xác thực bằng refresh token) | 200, 400, 401, 403, 415, 429, 500 |
| `GET /posts/{id}` | `posts:read` | 200, 304, 400, 401, 403, 404, 429, 500 |

## Rủi ro còn lại / việc cần làm

- Password flow của OAuth2 đã bị coi là lỗi thời (OAuth 2.1); nếu có client bên thứ ba, chuyển sang Authorization Code + PKCE.
- Chưa có cơ chế đăng xuất/thu hồi chủ động (`/auth/logout`) và MFA.
- Chưa có giám sát/cảnh báo khi phát hiện `REFRESH_TOKEN_REUSED` hoặc nhiều lần `401`.
