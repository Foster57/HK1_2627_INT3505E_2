"""LAB 3 — Build Newman-runnable collection & Error Case Verification.

Kiểm tra các yêu cầu của Lab 3:
- Bước A: Folder error-cases/ với 2 requests: POST thiếu title và GET /books/9999
- Bước B: Mỗi request có >= 2 test (1 cho status code, 1 cho body code/message)
- Bước C: Dùng collectionVariable lưu book_id từ POST cho DELETE request
"""
import json
from pathlib import Path
# pyrefly: ignore[missing-import]
import pytest


# =====================================================================
# 1. API Functional Tests cho 2 trường hợp lỗi của Lab 3 (Bước A & B)
# =====================================================================

def test_post_books_missing_title_step_b(client):
    """Bước B - Request 1: POST /books thiếu title.
    - Test 1 (Status code): HTTP 400 Bad Request
    - Test 2 (Body): code == 'VALIDATION_ERROR' và message == 'Invalid book data'
    """
    response = client.post(
        "/books",
        json={"author": "Dang Tran Tien"},
    )
    # Test 1: Status code
    assert response.status_code == 400

    # Test 2: Body (code và message)
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid book data"
    assert any(err["field"] == "title" for err in data.get("errors", []))


def test_get_books_9999_not_found_step_b(client):
    """Bước B - Request 2: GET /books/9999 không tồn tại.
    - Test 1 (Status code): HTTP 404 Not Found
    - Test 2 (Body): code == 'NOT_FOUND' và message == 'Book not found'
    """
    response = client.get("/books/9999")
    # Test 1: Status code
    assert response.status_code == 404

    # Test 2: Body (code và message)
    data = response.get_json()
    assert data["code"] == "NOT_FOUND"
    assert data["message"] == "Book not found"


# =====================================================================
# 2. API Test cho luồng Bước C: lưu book_id từ POST dùng cho DELETE
# =====================================================================

def test_post_then_delete_with_book_id_step_c(client):
    """Bước C: Lưu book_id sau khi POST để dùng cho DELETE."""
    # Tạo sách mới
    post_res = client.post(
        "/books",
        json={"title": "Test Book Lab 3", "author": "Tester", "year": 2024},
    )
    assert post_res.status_code == 201
    book_id = post_res.get_json()["id"]
    assert book_id > 0

    # Xóa sách với book_id vừa tạo
    del_res = client.delete(f"/books/{book_id}")
    assert del_res.status_code in (200, 204)

    # Kiểm tra lại chắc chắn sách đã bị xóa
    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 404


# =====================================================================
# 3. Kiểm tra tính hợp lệ của file books-api.postman_collection.json
# =====================================================================

def test_postman_collection_structure_lab03():
    """Kiểm tra file Postman collection đáp ứng chuẩn Lab 3 (Bước A, B, C)."""
    # Tìm file collection
    collection_path = Path(__file__).parent.parent / "books-api.postman_collection.json"
    if not collection_path.exists():
        collection_path = Path(__file__).parent.parent / "postman" / "books-api.postman_collection.json"

    assert collection_path.exists(), "Không tìm thấy file books-api.postman_collection.json"

    with open(collection_path, encoding="utf-8") as f:
        collection = json.load(f)

    # Bước A: Kiểm tra folder error-cases
    folders = {item["name"]: item for item in collection.get("item", [])}
    assert "error-cases" in folders, "Chưa tạo folder error-cases trong collection (Bước A)"

    error_items = folders["error-cases"].get("item", [])
    assert len(error_items) >= 2, "Folder error-cases phải có ít nhất 2 requests (Bước A)"

    # Bước B: Mỗi request trong error-cases phải có >= 2 test script (pm.test)
    for req in error_items:
        events = req.get("event", [])
        test_events = [e for e in events if e.get("listen") == "test"]
        assert len(test_events) > 0, f"Request '{req['name']}' thiếu tab Test script"

        script_lines = test_events[0].get("script", {}).get("exec", [])
        script_text = "\n".join(script_lines)
        pm_test_count = script_text.count("pm.test(")
        assert pm_test_count >= 2, (
            f"Request '{req['name']}' có {pm_test_count} pm.test (yêu cầu Bước B: >= 2)"
        )

    # Bước C: Kiểm tra biến book_id
    variables = [v.get("key") for v in collection.get("variable", [])]
    assert "book_id" in variables, "Collection thiếu variable 'book_id' (Bước C)"
