"""LAB 1 — add your five tests here. Do not delete the smoke tests.
A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

from copy import deepcopy
import pytest
from jsonschema import validate, ValidationError
from tools import get_book_schema


# Test A: GET /books khi database rỗng
def test_get_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.get_json() == []


# Test B: GET /books/9999 không tồn tại -> 404 và code NOT_FOUND
def test_get_book_not_found(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "NOT_FOUND"


# Test C: POST /books chỉ có author (thiếu title) -> 400, errors chứa title
def test_create_book_missing_title(client):
    response = client.post(
        "/books",
        json={"author": "Dang Tran Tien"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert any(err["field"] == "title" for err in data.get("errors", []))


# Test D: POST valid book, DELETE nó, GET lại cùng id -> 404
def test_delete_book_then_get_not_found(client):
    payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "year": 2008,
    }
    create_response = client.post("/books", json=payload)
    assert create_response.status_code == 201

    book_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code in (200, 204)

    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404


# BONUS: Validate response bằng JSON Schema; thêm field lạ vào bản copy và assert ValidationError
def test_response_extra_field_blocked(client):
    payload = {
        "title": "API Design Patterns",
        "author": "J.J. Geewax",
        "year": 2021,
        "isbn": "9781617297175",
    }
    response = client.post("/books", json=payload)
    assert response.status_code == 201

    book = response.get_json()
    schema = get_book_schema()

    # Response ban đầu phải hợp lệ
    validate(instance=book, schema=schema)

    # Tạo bản sao và thêm field lạ không được phép
    fake_book = deepcopy(book)
    fake_book["password_hash"] = "secret123"

    # Schema có additionalProperties: false nên phải bắn lỗi ValidationError
    with pytest.raises(ValidationError):
        validate(instance=fake_book, schema=schema)
