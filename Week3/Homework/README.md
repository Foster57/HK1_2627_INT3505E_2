# Review OpenWeather API theo 9 tiêu chí REST/API

## 1. Tổng quan

Đánh giá nhanh **OpenWeather API** theo 9 tiêu chí dùng trong buổi review chéo API.

> **Kết quả: 4/9 tiêu chí đạt**

| # | Tiêu chí | Kết quả | Nhận xét |
|---|---|:---:|---|
| 01 | Tài nguyên là danh từ | ✅ Đạt | `/weather`, `/forecast`, `/air_pollution` là các resource |
| 02 | Naming nhất quán | ✅ Đạt | Path lowercase, query parameter rõ ràng |
| 03 | Status code đúng nghĩa | ✅ Đạt | Có HTTP status/error code phù hợp |
| 04 | Idempotency rõ ràng | ✅ Đạt | Chủ yếu sử dụng `GET`, có tính idempotent |
| 05 | Error response có cấu trúc | ❌ Không đạt | Không theo RFC 7807 `problem+json` |
| 06 | Pagination rõ ràng | ❌ Không đạt | Không có pagination kiểu cursor/offset rõ ràng |
| 07 | Filter/Sort đa dạng | ❌ Không đạt | Không có hệ thống filter/sort resource đa dạng |
| 08 | Authentication & Security | ❌ Không đạt | API key truyền qua query parameter `appid` |
| 09 | Versioning + deprecation | ❌ Không đạt | Có version nhưng chưa theo convention version prefix ở đầu path |

---

## 2. Tiêu chí 01 — Tài nguyên là danh từ

### Kết quả: ✅ Đạt

OpenWeather sử dụng các endpoint biểu diễn resource bằng danh từ:

```http
GET /data/2.5/weather
GET /data/2.5/forecast
GET /data/2.5/air_pollution
```

Các từ như `weather`, `forecast`, `air_pollution` đều biểu diễn tài nguyên/dữ liệu cần truy cập.

Không sử dụng cách đặt endpoint theo hành động như:

```http
GET /getWeather
GET /getForecast
```

### Nhận xét

Cách thiết kế này phù hợp với nguyên tắc REST: **URL xác định resource, HTTP method thể hiện action**.

**→ Đạt.**

---

## 3. Tiêu chí 02 — Naming nhất quán

### Kết quả: ✅ Đạt

OpenWeather sử dụng cách đặt tên tương đối nhất quán:

```text
/data/2.5/weather
/data/2.5/forecast
```

Các query parameter cũng có ý nghĩa rõ ràng:

```text
lat
lon
appid
units
lang
```

Ví dụ:

```http
GET /data/2.5/weather?lat=21.0285&lon=105.8542&appid=YOUR_API_KEY&units=metric
```

### Nhận xét

- Path sử dụng lowercase.
- Resource có tên rõ nghĩa.
- Query parameter ngắn gọn và có ý nghĩa.

**→ Đạt.**

---

## 4. Tiêu chí 03 — Status code đúng nghĩa

### Kết quả: ✅ Đạt

OpenWeather sử dụng HTTP status code để biểu diễn kết quả request.

Ví dụ request thành công:

```http
200 OK
```

Response có thể chứa:

```json
{
  "cod": 200,
  "main": {
    "temp": 29.5
  }
}
```

Khi request gặp lỗi, API có thể trả về các HTTP error status tương ứng thay vì coi mọi request là thành công.

Ví dụ các nhóm lỗi thường gặp:

```text
401 Unauthorized
404 Not Found
429 Too Many Requests
5xx Server Error
```

> Lưu ý: trường `cod` trong JSON là thông tin do OpenWeather cung cấp; cần phân biệt nó với HTTP status code thực tế.

**→ Đạt.**

---

## 5. Tiêu chí 04 — Idempotency rõ ràng

### Kết quả: ✅ Đạt

OpenWeather chủ yếu cung cấp các API đọc dữ liệu:

```http
GET /data/2.5/weather
GET /data/2.5/forecast
```

Theo HTTP semantics, `GET` là method **safe** và **idempotent**.

Ví dụ:

```text
GET weather Hanoi
       ↓
Weather data

GET weather Hanoi
       ↓
Weather data
```

Việc thực hiện cùng một GET nhiều lần không tạo thêm resource hoặc thay đổi trạng thái server theo cách phụ thuộc vào số lần request.

Do API chủ yếu là read-only nên vấn đề idempotency của `POST`, `PUT`, `DELETE` không phải trọng tâm.

**→ Đạt.**

---

## 6. Tiêu chí 05 — Error response có cấu trúc

### Kết quả: ❌ Không đạt

Tiêu chí yêu cầu error response có cấu trúc nhất quán theo **RFC 7807 – Problem Details for HTTP APIs**, ví dụ:

```json
{
  "type": "https://example.com/errors/invalid-api-key",
  "title": "Invalid API Key",
  "detail": "The provided API key is invalid.",
  "instance": "/data/2.5/weather"
}
```

Trong khi OpenWeather sử dụng response lỗi đơn giản hơn, ví dụ:

```json
{
  "cod": 401,
  "message": "Invalid API key. Please see ..."
}
```

Response không cung cấp đầy đủ các trường chuẩn:

```text
type
title
detail
instance
```

### Vấn đề

- Không theo RFC 7807.
- Error schema đơn giản.
- Khó chuẩn hóa khi tích hợp với một hệ thống có nhiều API khác nhau.

**→ Không đạt.**

---

## 7. Tiêu chí 06 — Pagination rõ ràng

### Kết quả: ❌ Không đạt

Một số API của OpenWeather trả về nhiều bản ghi, ví dụ Forecast API sử dụng:

```json
{
  "cnt": 40,
  "list": [
    ...
  ]
}
```

`cnt` cho biết số lượng bản ghi nhưng không phải cơ chế pagination chuẩn.

Không có thiết kế phổ biến dạng:

```http
GET /forecast?page=1&limit=20
```

hoặc:

```http
GET /forecast?offset=20&limit=20
```

hoặc:

```http
GET /forecast?cursor=abc123
```

### Nhận xét

Checklist yêu cầu collection có pagination rõ ràng bằng cursor/offset và có giới hạn trên. OpenWeather không đáp ứng đầy đủ yêu cầu này.

**→ Không đạt.**

---

## 8. Tiêu chí 07 — Filter/Sort đa dạng

### Kết quả: ❌ Không đạt

OpenWeather có nhiều query parameter để xác định request, ví dụ:

```text
lat
lon
units
lang
appid
```

Một số API còn có tham số để loại bỏ một số phần dữ liệu trong response.

Tuy nhiên, đây chưa phải một hệ thống **filter/sort** đa dạng theo tiêu chí review.

Ví dụ API không cung cấp hệ thống query chuẩn dạng:

```http
GET /weather?filter[temp][gte]=30&filter[humidity][lt]=80
```

hoặc:

```http
GET /weather?sort=-temperature
```

### Nhận xét

API có parameter hóa request nhưng chưa thể hiện rõ cơ chế:

- Filter theo nhiều field.
- Sort theo nhiều field.
- Sparse fieldsets.

**→ Không đạt.**

---

## 9. Tiêu chí 08 — Authentication & Security

### Kết quả: ❌ Không đạt

OpenWeather sử dụng API key thông qua query parameter:

```http
GET /data/2.5/weather?lat=21.0285&lon=105.8542&appid=YOUR_API_KEY
```

Trong đó:

```text
appid=YOUR_API_KEY
```

chứa API key trực tiếp trong URL.

### Vấn đề

Theo checklist, yêu cầu:

> Token ở header, không lộ qua URL.

Thiết kế được ưu tiên hơn sẽ là:

```http
GET /weather

Authorization: Bearer YOUR_TOKEN
```

hoặc:

```http
X-API-Key: YOUR_API_KEY
```

API key trong URL có thể xuất hiện trong:

- Browser history.
- Proxy/access logs.
- Monitoring logs.
- Analytics systems.
- Các hệ thống trung gian khác.

### Nhận xét

Đây là điểm hạn chế đáng chú ý về security của API theo checklist đang sử dụng.

**→ Không đạt.**

---

## 10. Tiêu chí 09 — Versioning + Deprecation

### Kết quả: ❌ Không đạt

OpenWeather có versioning, ví dụ:

```http
/data/2.5/weather
/data/3.0/onecall
```

Như vậy API **có version**.

Tuy nhiên, checklist yêu cầu:

1. Có version prefix từ đầu URL.
2. Có lộ trình deprecation/ngừng hỗ trợ rõ ràng.

Trong khi OpenWeather sử dụng:

```text
/data/2.5/weather
```

thay vì convention:

```text
/v2.5/weather
```

hoặc:

```text
/v1/weather
```

Version không nằm ngay ở đầu path.

Ngoài ra, cách tổ chức version giữa các API/product khác nhau chưa hoàn toàn đồng nhất.

### Nhận xét

OpenWeather có cơ chế versioning nhưng **chưa đáp ứng đầy đủ convention của tiêu chí review**.

**→ Không đạt nếu chấm theo checklist nghiêm ngặt.**

---

# 11. Tổng kết

| Tiêu chí | Kết quả |
|---|:---:|
| 01. Tài nguyên là danh từ | ✅ |
| 02. Naming nhất quán | ✅ |
| 03. Status code đúng nghĩa | ✅ |
| 04. Idempotency rõ ràng | ✅ |
| 05. Error response có cấu trúc | ❌ |
| 06. Pagination rõ ràng | ❌ |
| 07. Filter/Sort đa dạng | ❌ |
| 08. Authentication & Security | ❌ |
| 09. Versioning + deprecation | ❌ |
| **Tổng** | **4/9 đạt** |

## Kết luận

> **OpenWeather API đạt 4/9 tiêu chí trong checklist review.**

### Điểm mạnh

- Resource được đặt tên theo danh từ.
- Naming tương đối nhất quán.
- Sử dụng HTTP status code.
- Các API đọc dữ liệu sử dụng `GET`, phù hợp với idempotency.

### Điểm cần cải thiện

1. **Error response** nên theo RFC 7807 `problem+json`.
2. **Pagination** nên có cursor/offset rõ ràng cho các collection lớn.
3. **Filter/Sort** nên cung cấp cơ chế query linh hoạt hơn.
4. **Authentication** nên truyền API credential qua header thay vì query string.
5. **Versioning** nên thống nhất convention và công bố deprecation lifecycle rõ ràng.

---

## 12. Feedback ngắn cho buổi review chéo

> OpenWeather API có thiết kế khá tốt ở resource naming, naming consistency, HTTP semantics và idempotency. Tuy nhiên API chưa đạt các tiêu chí về RFC 7807 error response, pagination, filter/sort đa dạng và authentication security do API key được truyền qua query parameter `appid`. API có versioning nhưng convention chưa hoàn toàn phù hợp với yêu cầu version prefix ở đầu path. **Tổng điểm: 4/9 tiêu chí đạt.**

---

## 13. Ví dụ Request

```http
GET /data/2.5/weather?lat=21.0285&lon=105.8542&appid=YOUR_API_KEY&units=metric
```

### Response thành công

```json
{
  "coord": {
    "lon": 105.8542,
    "lat": 21.0285
  },
  "weather": [
    {
      "main": "Clouds",
      "description": "broken clouds"
    }
  ],
  "main": {
    "temp": 29.5,
    "humidity": 78
  }
}
```

### Response lỗi

```json
{
  "cod": 401,
  "message": "Invalid API key. Please see ..."
}
```

---

## 14. Tài liệu tham khảo

- OpenWeather API Documentation: https://openweathermap.org/api
- Current Weather Data API: https://openweathermap.org/current
- Forecast API: https://openweathermap.org/forecast5
- RFC 7807 – Problem Details for HTTP APIs: https://www.rfc-editor.org/rfc/rfc7807
