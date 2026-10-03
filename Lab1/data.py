# =========================================================
# DATABASE GIẢ LẬP
# =========================================================

users = {
    1: {
        "id": 1,
        "username": "tien",
        "email": "tien@gmail.com"
    },
    2: {
        "id": 2,
        "username": "an",
        "email": "an@gmail.com"
    }
}

profiles = {
    1: {
        "user_id": 1,
        "full_name": "Dang Tran Tien",
        "bio": "Information System student"
    },
    2: {
        "user_id": 2,
        "full_name": "Nguyen Van An",
        "bio": "Software Engineer"
    }
}

posts = {
    1: {
        "id": 1,
        "title": "REST API cơ bản",
        "content": "REST là một kiến trúc cho web API.",
        "author_id": 1
    },
    2: {
        "id": 2,
        "title": "Học Flask",
        "content": "Flask là một web framework của Python.",
        "author_id": 2
    }
}

comments = {
    1: {
        "id": 1,
        "post_id": 1,
        "user_id": 2,
        "content": "Bài viết rất hữu ích!"
    }
}

tags = {
    1: {
        "id": 1,
        "name": "Python"
    },
    2: {
        "id": 2,
        "name": "REST"
    }
}

# Quan hệ nhiều-nhiều: post - tag
post_tags = {
    1: [1, 2],  # Post 1 gắn tag Python, REST
    2: [1]      # Post 2 gắn tag Python
}

# Quan hệ user theo dõi user khác
following = {
    1: [2],  # User 1 follow User 2
    2: []
}
