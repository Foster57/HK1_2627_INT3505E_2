# Báo Cáo Thực Hành Lab 3 — Build Newman-runnable Collection

## 1. Mục tiêu và Yêu cầu
- **Mục tiêu**: Xây dựng kịch bản kiểm thử tự động API bằng Postman Collection và chạy tự động thông qua công cụ dòng lệnh **Newman**.
- **Yêu cầu chi tiết**:
  - **A**: Bổ sung thư mục `error-cases/` với 2 requests: `POST /books` (thiếu `title`) và `GET /books/9999` (ID không tồn tại).
  - **B**: Mỗi request lỗi phải có ít nhất 2 `pm.test` (1 kiểm tra HTTP Status code, 1 kiểm tra JSON Body `code`/`message`).
  - **C**: Sử dụng `collectionVariable` để lưu trữ `book_id` từ kết quả của request `POST` và truyền vào request `DELETE`.
  - **D**: Chạy kiểm thử tự động bằng Newman với các reporter `cli` và `junit`, xuất kết quả ra file `reports/junit.xml`.

---

## 2. Câu lệnh thực thi (Execution Commands)

### Bước 1: Khởi động API Server (Terminal 1)
```powershell
cd "Week 8\lab08-starter"
python -m app --port 5000
```

### Bước 2: Chạy kiểm thử bằng Newman (Terminal 2)
```powershell
cd "Week 8\lab08-starter"
newman run books-api.postman_collection.json -e postman/local.postman_environment.json -r "cli,junit" --reporter-junit-export reports/junit.xml
```

---

## 3. Hình ảnh kết quả thực thi Newman

### Phần 1: Thực thi các request trong Collection
![Newman Run - Phần 1](./Test_lab03%20(1).png)

### Phần 2: Thống kê kết quả chạy và bảng Assertions
![Newman Run - Phần 2](./Test_lab03%20(2).png)

### Phần 3: Chi tiết log thực thi
![Newman Run - Phần 3](./Test_lab03%20(3).png)

### Phần 4: Log chi tiết các Error Cases
![Newman Run - Phần 4](./Test_lab03%20(4).png)

---

## 4. Báo cáo JUnit XML
Kết quả chạy kiểm thử được xuất tự động ra file [reports/junit.xml](../reports/junit.xml) gồm:
- **Tổng số request**: 7 (5 happy-path + 2 error-cases).
- **Tổng số assertions (`pm.test`)**: 14 test cases.
- **Thời gian thực thi**: < 10 giây (đạt chuẩn yêu cầu của bài thực hành).
