# Lab 4 — Phân tích kết quả Load Test Books API với Locust

## 1. Bảng số liệu đo thực tế từ 3 kịch bản

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| **A** (Baseline) | 10 | 2 | 30s | **18 ms** | 0.00% (0/141) | 4.76 |
| **B** (Load test) | 50 | 5 | 60s | **20 ms** | 0.36% (5/1399) | 23.46 |
| **C** (Spike test) | 200 | 50 | 30s | **90 ms** | 0.18% (5/2846) | 95.98 |

### Chi tiết số liệu theo từng Endpoint

#### Kịch bản A (10 users, 2 spawn/s, 30s):
- `GET /books`: 43 requests, 0 fails, RPS = 1.45, Avg = 5.2ms, Median = 5ms, p95 = 8ms, Max = 10ms.
- `GET /books/{id}`: 51 requests, 0 fails, RPS = 1.72, Avg = 5.4ms, Median = 5ms, p95 = 7ms, Max = 8ms.
- `GET /books?year=[year]`: 30 requests, 0 fails, RPS = 1.01, Avg = 7.1ms, Median = 5ms, p95 = 22ms, Max = 27ms.
- `POST /books`: 17 requests, 0 fails, RPS = 0.57, Avg = 18.7ms, Median = 17ms, p95 = 28ms, Max = 28ms.
- **Aggregated**: 141 requests, 0 fails (0.00%), RPS = 4.76, Avg = 7.3ms, p50 = 5ms, p95 = 18ms, Max = 28ms.

#### Kịch bản B (50 users, 5 spawn/s, 60s):
- `GET /books`: 537 requests, 0 fails, RPS = 9.01, Avg = 6.3ms, Median = 6ms, p95 = 12ms, Max = 31ms.
- `GET /books/{id}`: 328 requests, 0 fails, RPS = 5.50, Avg = 6.0ms, Median = 5ms, p95 = 10ms, Max = 34ms.
- `GET /books?year=[year]`: 375 requests, 5 fails (1.33%), RPS = 6.29, Avg = 5.8ms, Median = 5ms, p95 = 9ms, Max = 19ms.
- `POST /books`: 159 requests, 0 fails, RPS = 2.67, Avg = 19.9ms, Median = 18ms, p95 = 35ms, Max = 43ms.
- **Aggregated**: 1399 requests, 5 fails (0.36%), RPS = 23.46, Avg = 7.7ms, p50 = 6ms, p95 = 20ms, Max = 43ms.

#### Kịch bản C (200 users, 50 spawn/s, 30s):
- `GET /books`: 1035 requests, 0 fails, RPS = 34.90, Avg = 21.7ms, Median = 9ms, p95 = 99ms, p99 = 240ms, Max = 331ms.
- `GET /books/{id}`: 747 requests, 0 fails, RPS = 25.19, Avg = 17.3ms, Median = 8ms, p95 = 74ms, p99 = 140ms, Max = 317ms.
- `GET /books?year=[year]`: 694 requests, 5 fails (0.72%), RPS = 23.40, Avg = 17.5ms, Median = 8ms, p95 = 78ms, p99 = 170ms, Max = 227ms.
- `POST /books`: 370 requests, 0 fails, RPS = 12.48, Avg = 40.6ms, Median = 22ms, p95 = 150ms, p99 = 280ms, Max = 310ms.
- **Aggregated**: 2846 requests, 5 fails (0.18%), RPS = 95.98, Avg = 22.0ms, p50 = 9ms, p95 = 90ms, p99 = 210ms, Max = 331ms.

---

## 2. Trả lời các câu hỏi phân tích

### Câu 1: Trong 3 kịch bản, kịch bản nào có p95 cao nhất? Vì sao?
- **Kịch bản có p95 cao nhất**: **Kịch bản C (Spike test - 200 users)** với `p95 = 90 ms` (và ở endpoint `POST /books`, p95 lên tới `150 ms`, p99 lên tới `280 ms`, max response time lên tới `331 ms`).
- **Giải thích nguyên nhân dựa trên số liệu quan sát**:
  1. **Tải tăng đột biến (Spike Load) & Hiện tượng nghẽn hàng đợi (Queueing Delay)**: Trong kịch bản C, số lượng user tăng vọt lên 200 với spawn rate rất cao (50 users/giây). Hệ thống phải xử lý xấp xỉ 96 request/giây (so với 4.76 RPS ở kịch bản A và 23.46 RPS ở kịch bản B).
  2. **Bản chất của máy chủ Flask development server (Werkzeug)**: Server chạy ở chế độ dev là server đơn tiến trình (single-process) hoặc đa luồng giới hạn. Khi 200 người dùng đồng thời dồn dập gửi yêu cầu, hàng đợi xử lý request tại socket TCP và tầng WSGI bị ứ đọng.
  3. **Cơ sở dữ liệu SQLite**: SQLite sử dụng cơ chế khóa file đơn giản (file-level locking). Đối với các tác vụ ghi (`POST /books`), việc commit dữ liệu yêu cầu độc quyền ghi file, dẫn đến việc các thao tác đọc và ghi khác phải xếp hàng chờ đợi, đẩy độ trễ đuôi (tail latency như p95, p99) tăng vọt.
  4. **Quy luật tăng phi tuyến của p95 (Hockey-stick Curve)**:
     - Khi số user tăng từ 10 lên 50 (tăng 5 lần), p95 chỉ tăng nhẹ từ 18 ms lên 20 ms (+11%) do hệ thống vẫn nằm dưới ngưỡng bão hòa (saturation point).
     - Khi số user tăng lên 200 (tăng gấp 4 lần so với kịch bản B), p95 tăng vọt từ 20 ms lên 90 ms (+350%), và p99 tăng lên 210 ms. Điều này phản ánh chính xác quy luật đường cong bão hòa phi tuyến trong lý thuyết hàng đợi (Queueing Theory / Little's Law).

#### Đồ thị minh họa: Đường biểu diễn p95 theo số user (Phi tuyến sau ngưỡng bão hòa)

```text
p95 (ms)
  100 |                                          * (200 users, 90ms)
   90 |                                         /
   80 |                                        /
   70 |                                       /
   60 |                                      /
   50 |                                     /
   40 |                                    /
   30 |                                   /
   20 |                * (50 users, 20ms)/
   10 |   * (10u, 18ms)
    0 +------------------------------------------
          10          50                        200    Users
```

---

### Câu 2: Có endpoint nào fail rate tăng theo số user? Đoán nguyên nhân dựa trên code.
- **Quan sát từ kết quả đo**:
  - Endpoint duy nhất ghi nhận failure trong cả 3 kịch bản là `GET /books?year=[year]`:
    - Kịch bản A (10 user): 0 lỗi / 30 req (0.00% - do số lượng mẫu nhỏ, xác suất 1% chưa trúng mẫu).
    - Kịch bản B (50 user): 5 lỗi / 375 req (~1.33%).
    - Kịch bản C (200 user): 5 lỗi / 694 req (~0.72%).
- **Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust**:
  - **Lỗi đánh dấu trong Locust**: Các failure quan sát được ở trên **hoàn toàn là do phía client Locust cố ý đánh dấu** thông qua `catch_response=True` và `response.failure("500 Internal Server Error (simulated)")` theo xác suất ~1% trong file `locustfile.py`:
    ```python
    @task(2)
    def search_by_year(self, year=None):
        if year is None:
            year = random.choice([2020, 2021, 2022, 2023])
        with self.client.get(
            f"/books?year={year}", name="GET /books?year=[year]", catch_response=True
        ) as response:
            # 1% fail rate (giả lập 500)
            if random.random() < 0.01:
                response.failure("500 Internal Server Error (simulated)")
            elif response.status_code == 200:
                response.success()
    ```
    Thực tế, máy chủ Flask vẫn xử lý và trả về mã trạng thái HTTP 200 OK. Lỗi này là lỗi mô phỏng (client-side simulated assertion failure).
  - **Lỗi HTTP thực từ code server**:
    - Trong bài đo thực tế, **không có endpoint nào sinh lỗi HTTP thực tế (500 hay timeout)** vì tài nguyên máy cá nhân đủ mạnh để xử lý 2846 request mà không bị crash hay drop kết nối.
    - **Phân tích dựa trên code `app.py`**:
      1. **Rủi ro SQLite Concurrency Lock trên `POST /books`**:
         ```python
         @app.post("/books")
         def create_book():
             data = parse_book()
             book = Book(**data)
             db.session.add(book)
             try:
                 db.session.commit()
             except IntegrityError:
                 db.session.rollback()
                 return error(409, "CONFLICT", "ISBN already exists")
         ```
         Trong code, việc commit ghi vào SQLite chỉ xử lý ngoại lệ `IntegrityError` (báo mã 409). Nếu số lượng user tăng quá cao hoặc thời gian giữ khóa ghi kéo dài, SQLite sẽ ném ngoại lệ `sqlite3.OperationalError: database is locked`, không được bắt trong `try...except` này, dẫn đến máy chủ trả về mã HTTP 500 thực sự (Internal Server Error).
      2. **Endpoint `GET /books/<book_id>`**:
         Trong `locustfile.py`, `read_book` sinh ngẫu nhiên `book_id = random.randint(1, 50)`. Khi ID không tồn tại, server trả về mã `404 NOT_FOUND`. Code Locust đã chủ động xử lý `if response.status_code in (200, 404): response.success()` nên mã 404 không bị tính là lỗi vận hành.

---

### Câu 3: Nếu prod cần SLO p95 < 300ms, kịch bản nào đạt? Đề xuất baseline cho CI gate.
- **Đánh giá theo SLO p95 < 300ms**:
  - Cả **3 kịch bản A, B, C đều đạt SLO p95 < 300ms**:
    - Kịch bản A: p95 = **18 ms** (< 300 ms) -> **Đạt**.
    - Kịch bản B: p95 = **20 ms** (< 300 ms) -> **Đạt**.
    - Kịch bản C: p95 = **90 ms** (< 300 ms) -> **Đạt**.
  - *Lưu ý cảnh báo*: Mặc dù kịch bản C có p95 đạt 90 ms, nhưng thời gian đáp ứng tối đa (`Max response time`) đã đạt **331 ms**, và `p99 = 210 ms`. Ở endpoint `POST /books`, p95 đã lên tới **150 ms** và p99 lên tới **280 ms**. Điều này cho thấy hệ thống đã tiệm cận sát ngưỡng giới hạn chấp nhận được khi có tải tăng vọt.
- **Đề xuất baseline cho CI gate**:
  - Trên môi trường CI/CD (như GitHub Actions runner với tài nguyên hạn chế 2 vCPU, RAM chia sẻ):
    - Không nên chạy kịch bản C (200 user) trong mỗi Pull Request vì dễ gây quá tải runner, làm test bị flaky do tranh chấp CPU ảo.
    - **Baseline phù hợp cho CI gate**:
      - Cấu hình tải: **20 concurrent users, spawn rate 5, thời gian 30s** (`-u 20 -r 5 -t 30s`).
      - Tiêu chí chặn (Quality Gate threshold):
        1. **p95 < 80 ms** (với tải 20 user).
        2. **RPS >= 15 req/s**.
        3. **HTTP Failure Rate (Real Errors) = 0%** (ngoại trừ các lỗi giả lập kiểm thử).
    - Kịch bản C (Spike test) và Kịch bản B (Soak/Load test) nên được đưa vào pipeline chạy định kỳ ban đêm (Nightly CI Performance Job) hoặc trước khi phát hành phiên bản mới (Release Pipeline).
- **Giới hạn của phép đo**:
  - Không khẳng định hiệu năng production từ kết quả này vì:
    - Test chạy trên localhost qua loopback interface (`127.0.0.1`), không có độ trễ mạng thực tế, bắt tay SSL/TLS, DNS lookup, hay mất gói tin.
    - Sử dụng Flask development server (chạy đơn tiến trình) thay vì các production WSGI/ASGI server như Gunicorn/Uvicorn kết hợp Nginx reverse proxy.
    - Sử dụng SQLite file cục bộ thay vì hệ quản trị CSDL quan hệ phân tán hoặc client-server (PostgreSQL/MySQL) có connection pool mạng thực tế.

---

### Câu hỏi bonus: Nếu connection pool giới hạn 5, điều gì xảy ra khi 200 user truy cập đồng thời? Làm thế nào để xác nhận bằng Locust?

#### 1. Điều gì xảy ra khi connection pool bị giới hạn ở 5 và có 200 user truy cập đồng thời?
1. **Nghẽn kết nối (Connection Pool Starvation / Exhaustion)**:
   - Hồ bơi kết nối (Connection Pool) chỉ cung cấp tối đa 5 kết nối đồng thời tới cơ sở dữ liệu.
   - Khi có 200 user gửi request liên tục, chỉ có 5 request được cấp connection để truy vấn DB tại một thời điểm. 195 request còn lại buộc phải xếp hàng chờ trong hàng đợi kết nối của SQLAlchemy (`QueuePool`).
2. **Độ trễ tăng vọt (Latency Explosion)**:
   - Thời gian phản hồi (đặc biệt là p95, p99 và Max response time) sẽ tăng vọt tương ứng với thời gian chờ kết nối rảnh trong pool.
3. **Lỗi Timeout và sụp đổ dịch vụ (HTTP 500 / 503 / 504)**:
   - Nếu thời gian chờ trong hàng đợi vượt quá thời gian chờ tối đa (`pool_timeout`, mặc định của SQLAlchemy là 30 giây), SQLAlchemy sẽ ném lỗi:
     `sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 0 reached, connection timed out, timeout 30.00`
   - Máy chủ API không thể kết nối tới DB và sẽ trả về HTTP 500 (Internal Server Error) cho hàng loạt request, khiến tỷ lệ lỗi (Failure Rate) tăng vọt.
4. **Giới hạn thông lượng (Throughput Throttling)**:
   - RPS của hệ thống sẽ bị khống chế ở một mức trần tuyệt đối, tính bằng công thức:
     $$\text{Max RPS} \approx \frac{\text{Pool Size}}{\text{Average Query Execution Time}}$$

#### 2. Làm thế nào để xác nhận hiện tượng trên bằng Locust?
- **Bước 1: Cấu hình giới hạn Connection Pool trên Server (app.py)**:
  Cấu hình SQLAlchemy engine options với `pool_size=5`, `max_overflow=0`, và đặt `pool_timeout` ngắn (ví dụ 1 đến 2 giây) để dễ quan sát timeout:
  ```python
  app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
      "pool_size": 5,
      "max_overflow": 0,
      "pool_timeout": 2.0,  # Timeout sau 2 giây chờ kết nối
  }
  ```
  *(Lưu ý: Chạy trên CSDL hỗ trợ connection pooling thực tế như PostgreSQL hoặc cấu hình QueuePool cho ứng dụng).*
- **Bước 2: Thiết lập kịch bản Locust**:
  Chạy kịch bản tải cao hoặc spike test tương đương kịch bản C:
  ```bash
  locust -f locustfile.py --headless -u 200 -r 50 -t 30s --html reports/pool_test.html
  ```
- **Bước 3: Các dấu hiệu xác nhận trên báo cáo Locust (HTML Report)**:
  1. **Tab Failures**: Xuất hiện hàng loạt lỗi HTTP 500 kèm thông điệp lỗi `TimeoutError: QueuePool limit...`.
  2. **Biểu đồ Response Times**: Đường 95th Percentile và Median tăng vọt lên mức sát ngưỡng `pool_timeout` (~2000 ms) hoặc cao hơn.
  3. **Biểu đồ Total Requests per Second (RPS)**: Đường đồ thị RPS bị kẹt ngang ở mức trần không thể tăng lên dù số lượng user tiếp tục tăng.
  4. **Tỷ lệ thất bại (Failure Rate)**: Tỷ lệ lỗi tăng đột biến theo số user, tiệm cận các giá trị cao (có thể lên tới 50% - 80% khi hàng đợi cạn kiệt).
