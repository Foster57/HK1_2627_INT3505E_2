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
from models import Book
from jsonschema import validate, ValidationError
import pytest
from tools import get_book_schema

"Test A"
def test_get_book (client):
    respone = client.get("/books")
    assert respone.status_code == 200
    assert respone.get_json() == []

"Test B"
def test_post_book (client): 
    respone = client.post("/books/999")
    assert respone.status_code == 404
    data = respone.get_json()
    assert data["code"] == "Not Found"

"Test C"
def test_create_book_missing_title(client):
    response = client.post(
        "/books",
        json={
            "author": "Dang Tran Tien"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "title" in data["errors"]

"Test D"

def test_delete_book_then_get_books (client, sample_book):
   
    create_response = client.post(
        "/books",
        json=sample_book
    )

    assert create_response.status_code == 201

    book = create_response.get_json()
    book_id = book["id"]


    delete_response = client.delete(
        f"/books/{book_id}"
    )

    assert delete_response.status_code in (200, 204)

    get_response = client.get(
        f"/books/{book_id}"
    )

    assert get_response.status_code == 404
