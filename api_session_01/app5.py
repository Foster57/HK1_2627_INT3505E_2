from flask import Flask, jsonify, request

app = Flask(__name__)
_next = 2
BOOKS = [{"id": 1, "title": "Clean Code", "author": "R. Martin"}]

def find(bid):
    return next((b for b in BOOKS if b["id"] == bid), None)

@app.route("/books", methods=["GET"])
def list_books():
    result = BOOKS[:]
    # (a) search: GET /books?q=...
    q = request.args.get("q", "").strip().lower()
    if q:
        result = [b for b in result
                  if q in b["title"].lower()
                  or q in b["author"].lower()]
    # (b) sort: GET /books?sort=title|author|year
    sort_key = request.args.get("sort")
    if sort_key and sort_key in ("title", "author", "year"):
        result = sorted(result, key=lambda b: b.get(sort_key, ""))
    n = int(request.args.get("limit", 100))
    return jsonify(result[:n]), 200


@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)
    if not book: return {"error": "not found"}, 404
    return jsonify(book), 200


def validate_year(body):
    """(c) year phải là số >= 1900 nếu có truyền."""
    if "year" in body:
        try:
            y = int(body["year"])
        except (ValueError, TypeError):
            return "year must be an integer"
        if y < 1900:
            return "year must be >= 1900"
    return None

@app.route("/books", methods=["POST"])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    t, a = body.get("title"), body.get("author")
    if not t or not a:
        return {"error": "need title+author"}, 400
    err = validate_year(body)
    if err:
        return {"error": err}, 400
    year = int(body["year"]) if "year" in body else None
    book = {"id": _next, "title": t, "author": a}
    if year is not None:
        book["year"] = year
    _next += 1; BOOKS.append(book)
    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}

@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book: return {"error": "not found"}, 404
    if request.method == "PUT":
        body = request.get_json(silent=True) or {}
        err = validate_year(body)
        if err:
            return {"error": err}, 400
        if "year" in body:
            body["year"] = int(body["year"])
        book.update(body)
        return jsonify(book), 200
    BOOKS.remove(book)
    return "", 204
    
if __name__ == "__main__":
    app.run(host="[IP_ADDRESS]", port=5000, debug=True)