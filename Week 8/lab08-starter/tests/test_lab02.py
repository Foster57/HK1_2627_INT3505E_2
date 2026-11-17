"""LAB 2 — Contract Testing: OpenAPI validation & Response Verification with jsonschema."""
from pathlib import Path
import pytest
import yaml
from jsonschema import validate
from tools import get_book_schema


def get_openapi_spec():
    spec_path = Path(__file__).parent.parent / "openapi.yaml"
    return yaml.safe_load(spec_path.read_text(encoding="utf-8"))


# --- 1. Kiểm tra 3 lỗi đã được sửa trong file openapi.yaml ---

def test_spec_all_operations_have_operation_id():
    """Kiểm tra Lỗi 1: Mọi endpoint (kể cả GET /books) đều phải có operationId."""
    spec = get_openapi_spec()
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                assert "operationId" in op, f"{method.upper()} {path} thiếu operationId"


def test_spec_204_has_no_content():
    """Kiểm tra Lỗi 2: Response 204 không được khai báo content/body."""
    spec = get_openapi_spec()
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                responses = op.get("responses", {})
                if "204" in responses:
                    assert "content" not in responses["204"], (
                        f"{method.upper()} {path} response 204 không được phép có content"
                    )


def test_spec_book_year_is_integer():
    """Kiểm tra Lỗi 3: Book.year phải có kiểu integer khớp với model Python."""
    schema = get_book_schema()
    year_prop = schema["properties"]["year"]
    assert year_prop.get("type") == "integer", "Book.year schema phải là type: integer"


# --- 2. Đối chiếu thực tế giữa API Response và OpenAPI Schema ---

def test_get_books_matches_openapi_contract(client):
    """GET /books phải trả về danh sách các Book hợp lệ theo schema."""
    client.post(
        "/books",
        json={"title": "Contract Testing", "author": "QA Team", "year": 2024, "isbn": "9781234567890"},
    )
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

    book_schema = get_book_schema()
    for item in data:
        validate(instance=item, schema=book_schema)


def test_create_and_get_book_matches_contract(client):
    """POST /books và GET /books/{id} phải trả về đúng schema Book."""
    create_res = client.post(
        "/books",
        json={"title": "Python in Depth", "author": "Guido", "year": 2020, "isbn": "9780123456789"},
    )
    assert create_res.status_code == 201
    created_book = create_res.get_json()

    book_schema = get_book_schema()
    validate(instance=created_book, schema=book_schema)

    get_res = client.get(f"/books/{created_book['id']}")
    assert get_res.status_code == 200
    validate(instance=get_res.get_json(), schema=book_schema)


def test_delete_book_response_has_empty_body(client, sample_book):
    """DELETE /books/{id} trả về HTTP 204 và KHÔNG có response body theo chuẩn HTTP."""
    res = client.delete(f"/books/{sample_book}")
    assert res.status_code == 204
    assert res.data == b"", "Response 204 không được chứa dữ liệu trong body"


def test_error_response_matches_contract(client):
    """Lỗi 404 phải khớp với Error schema trong OpenAPI."""
    res = client.get("/books/99999")
    assert res.status_code == 404
    data = res.get_json()

    spec = get_openapi_spec()
    error_schema = spec["components"]["schemas"]["Error"]
    validate(instance=data, schema=error_schema)
