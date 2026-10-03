# Blog REST API

Nền tảng blog đơn giản cho phép người dùng đăng **bài viết (posts)**, mỗi bài có **bình luận (comments)** và gắn **thẻ (tags)**. Mỗi user có **hồ sơ (profile)** và đăng ký **theo dõi (follow)** tác giả khác.

---

## 1. Xác định Resources trong miền

| Resource     | Loại              | Mô tả                                      |
| ------------ | ----------------- | ------------------------------------------- |
| **Users**    | Collection + Item | Người dùng hệ thống                         |
| **Profile**  | Singular          | Hồ sơ cá nhân (1-1 với User)                |
| **Following**| Collection        | Danh sách user đang theo dõi (thuộc về User) |
| **Posts**    | Collection + Item | Bài viết                                    |
| **Comments** | Collection        | Bình luận (thuộc về Post)                    |
| **Tags**     | Collection + Item | Thẻ phân loại                               |
| **Post-Tags**| Collection        | Quan hệ nhiều-nhiều giữa Post và Tag         |

---

## 2. Phân loại Collection / Item / Sub-resource

```
Resource chính (top-level):
  ├── Users       → collection (/users) + item (/users/:id)
  ├── Posts        → collection (/posts) + item (/posts/:id)
  └── Tags         → collection (/tags)  + item (/tags/:id)

Sub-resource (phụ thuộc vào resource cha):
  ├── Profile      → singular sub-resource của User   (1 user → 1 profile)
  ├── Following    → collection sub-resource của User  (1 user → nhiều following)
  ├── Comments     → collection sub-resource của Post  (1 post → nhiều comments)
  └── Post-Tags    → collection sub-resource của Post  (nhiều-nhiều: post ↔ tag)
```

---

## 3. Quyết định Version Segment

### Chọn: **URI Path Versioning** → `/api/v1/`

| Phương pháp          | Ví dụ                                      | Ưu điểm               | Nhược điểm                  |
| -------------------- | ------------------------------------------- | ---------------------- | --------------------------- |
| **URI Path**       | `/api/v1/users`                             | Rõ ràng, dễ đọc        | URL thay đổi khi lên version |
| Query Parameter      | `/api/users?version=1`                      | Không đổi URL gốc      | Dễ bỏ sót, khó cache        |
| Header               | `Accept: application/vnd.blog.v1+json`      | URL sạch               | Khó test bằng trình duyệt   |

**Lý do chọn URI Path:**
- **Trực quan**: Nhìn URL biết ngay version nào → `/api/v1/users` vs `/api/v2/users`
- **Dễ routing**: Flask route mapping đơn giản, không cần middleware phân tích header
- **Dễ test**: Gõ trực tiếp trên trình duyệt hoặc Postman
- **Phổ biến**: GitHub, Twitter/X, Stripe, Google đều dùng cách này

---

## 4. Sơ đồ cây Endpoint

```
/api/v1/
│
├── users ................................................ [Collection]
│   │   GET     → Lấy danh sách tất cả users
│   │   POST    → Tạo user mới
│   │
│   └── /:user_id ........................................ [Item]
│       │   GET     → Lấy 1 user
│       │   PUT     → Thay thế toàn bộ user
│       │   PATCH   → Cập nhật 1 phần user
│       │   DELETE  → Xóa user (cascade: profile, following)
│       │
│       ├── /profile ..................................... [Singular Sub-resource]
│       │       GET     → Lấy profile của user
│       │       PUT     → Tạo/cập nhật profile
│       │
│       └── /following ................................... [Collection Sub-resource]
│           │   GET     → Danh sách user đang follow
│           │   POST    → Follow user khác
│           │
│           └── /:target_id .............................. [Item]
│                   DELETE  → Unfollow user
│
├── posts ................................................ [Collection]
│   │   GET     → Lấy danh sách posts (?author_id= filter)
│   │   POST    → Tạo post mới
│   │
│   └── /:post_id ........................................ [Item]
│       │   GET     → Lấy 1 post
│       │   PUT     → Thay thế toàn bộ post
│       │   PATCH   → Cập nhật 1 phần post
│       │   DELETE  → Xóa post (cascade: comments, post_tags)
│       │
│       ├── /comments .................................... [Collection Sub-resource]
│       │   │   GET     → Lấy comments của post
│       │   │   POST    → Tạo comment mới
│       │   │
│       │   └── /:comment_id ............................. [Item]
│       │           DELETE  → Xóa comment
│       │
│       └── /tags ........................................ [Collection Sub-resource]
│           │   GET     → Lấy tags của post
│           │   POST    → Gắn tag vào post
│           │
│           └── /:tag_id ................................. [Item]
│                   DELETE  → Gỡ tag khỏi post
│
└── tags ................................................. [Collection]
        GET     → Lấy danh sách tất cả tags
        POST    → Tạo tag mới
```

---


---
