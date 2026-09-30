from flask import Flask, jsonify

app = Flask(__name__)

ORDERS = {
    "1": {"id": "1", "product_id": 10, "quantity": 3, "status": "pending"},
    "2": {"id": "2", "product_id": 11, "quantity": 5, "status": "shipped"},
    "3": {"id": "3", "product_id": 12, "quantity": 8, "status": "delivered"},
}

@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(ORDERS)


@app.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": "not found"}, 404
    if order["status"] in ("shipped", "delivered"):
        return {"error": "cannot delete"}, 409
    ORDERS.pop(order_id, None)
    return "Delete successfully", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)