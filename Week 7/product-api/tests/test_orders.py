def test_create_order_success(client):
    """Test creating an order with valid products."""
    # First create products
    p1 = client.post("/products/", json={"name": "Book A", "price": 12.5}).get_json()
    p2 = client.post("/products/", json={"name": "Book B", "price": 25.0}).get_json()

    order_payload = {
        "customer_name": "Alice Smith",
        "items": [
            {"product_id": p1["id"], "quantity": 2},
            {"product_id": p2["id"], "quantity": 1},
        ],
    }

    res = client.post("/orders/", json=order_payload)
    assert res.status_code == 201
    order = res.get_json()
    assert order["customer_name"] == "Alice Smith"
    assert order["status"] == "pending"
    # 2 * 12.5 + 1 * 25.0 = 50.0
    assert order["total_price"] == 50.0
    assert len(order["items"]) == 2


def test_create_order_product_not_found(client):
    """Test creating order with nonexistent product returns 404."""
    order_payload = {
        "customer_name": "Bob",
        "items": [
            {"product_id": 9999, "quantity": 1},
        ],
    }
    res = client.post("/orders/", json=order_payload)
    assert res.status_code == 404


def test_update_order_status(client):
    """Test updating order status."""
    p = client.post("/products/", json={"name": "Item X", "price": 10.0}).get_json()
    order = client.post(
        "/orders/",
        json={"customer_name": "Charlie", "items": [{"product_id": p["id"], "quantity": 1}]},
    ).get_json()

    patch_res = client.patch(
        f"/orders/{order['id']}/status",
        json={"status": "completed"},
    )
    assert patch_res.status_code == 200
    assert patch_res.get_json()["status"] == "completed"


def test_order_not_found(client):
    """Test 404 when querying nonexistent order."""
    res = client.get("/orders/9999")
    assert res.status_code == 404

