from flask import Flask, jsonify, request

app = Flask(__name__)


BOOKS = [
    {"id": "1", "t": "Python Basics"},
    {"id": "2", "t": "Flask Web Development"},
    {"id": "3", "t": "Advanced Python"},
    {"id": "4", "t": "Data Structures and Algorithms in Python"},
    {"id": "5", "t": "Python for Data Science"},
]

def find_by_id(book_id):
    return next((b for b in BOOKS if str(b["id"]) == str(book_id)), None)

@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200


@app.route("/items/<int:item_id>")
def get_item(item_id):  
    return jsonify({"id": item_id}), 200

@app.route("/books", methods=["GET"])
def list_books():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    items = [b for b in BOOKS if q in b["t"].lower()][:limit]
    return jsonify({"items": items}), 200
    # offset, dùng cho buổi 5
    # offset=int(request.args.get("offset",0))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)