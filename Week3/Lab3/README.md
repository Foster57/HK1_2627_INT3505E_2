# Lab 3: Triển khai /orders có Cursor Pagination

Triển khai API `GET /orders` hỗ trợ phân trang theo cursor, lọc, sắp xếp và chọn trường dữ liệu (sparse fieldsets).

---

## 1. Khởi chạy Server

```bash
python app.py
```

Server chạy mặc định tại: `http://localhost:5000`

---

## 2. API Reference: `GET /orders`

| Tham số | Kiểu | Mô tả | Ví dụ |
| :--- | :--- | :--- | :--- |
| `limit` | int | Số lượng bản ghi mỗi trang (mặc định 10) | `?limit=5` |
| `cursor` | string | Chuỗi base64 cursor để lấy trang tiếp theo | `?cursor=eyJpZCI6IDV9` |
| `status` | string | Lọc theo trạng thái order | `?status=paid` |
| `customer_id` | string | Lọc theo ID khách hàng | `?customer_id=c1` |
| `sort` | string | Trường sắp xếp (thêm `-` để sắp xếp giảm dần) | `?sort=-total` |
| `fields` | string | Danh sách trường cần lấy, phân cách bằng dấu phẩy | `?fields=id,total` |

---

## 3. Lệnh kiểm thử (cURL)

### 3.1. Lọc theo trạng thái (`status`)
```bash
curl "http://localhost:5000/orders?status=paid"
```

### 3.2. Phân trang theo Cursor (`limit` & `cursor`)
* Lấy 5 phần tử đầu tiên:
```bash
curl "http://localhost:5000/orders?limit=5"
```
* Lấy trang tiếp theo với `next_cursor` nhận được từ response:
```bash
curl "http://localhost:5000/orders?limit=5&cursor=eyJpZCI6IDV9"
```

### 3.3. Sparse Fieldsets (`fields`)
Chỉ lấy `id` và `total`:
```bash
curl "http://localhost:5000/orders?fields=id,total"
```

### 3.4. Sắp xếp (`sort`)
Sắp xếp theo `total` giảm dần:
```bash
curl "http://localhost:5000/orders?sort=-total"
```

### 3.5. Kiểm thử Cursor hỏng (Trả về 400 Bad Request)
```bash
curl -i "http://localhost:5000/orders?cursor=invalid_cursor"
```
