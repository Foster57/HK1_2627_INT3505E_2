def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "healthy"


def test_create_and_get_product(client):
    """Test product creation and retrieval."""
    payload = {
        "name": "Mechanical Keyboard",
        "price": 89.99,
        "description": "RGB mechanical gaming keyboard",
        "stock": 15,
    }
    # Create product
    res = client.post("/products/", json=payload)
    assert res.status_code == 201
    created = res.get_json()
    assert created["id"] is not None
    assert created["name"] == payload["name"]
    assert created["price"] == payload["price"]

    # Get product list
    list_res = client.get("/products/")
    assert list_res.status_code == 200
    items = list_res.get_json()
    assert len(items) == 1
    assert items[0]["name"] == "Mechanical Keyboard"

    # Get single product by id
    item_res = client.get(f"/products/{created['id']}")
    assert item_res.status_code == 200
    assert item_res.get_json()["name"] == "Mechanical Keyboard"


def test_update_product(client):
    """Test updating a product."""
    create_res = client.post(
        "/products/",
        json={"name": "Old Mouse", "price": 10.0, "stock": 5},
    )
    product_id = create_res.get_json()["id"]

    update_res = client.put(
        f"/products/{product_id}",
        json={"name": "Wireless Mouse", "price": 19.99},
    )
    assert update_res.status_code == 200
    updated = update_res.get_json()
    assert updated["name"] == "Wireless Mouse"
    assert updated["price"] == 19.99


def test_delete_product(client):
    """Test deleting a product."""
    create_res = client.post(
        "/products/",
        json={"name": "Disposable Item", "price": 5.0, "stock": 1},
    )
    product_id = create_res.get_json()["id"]

    del_res = client.delete(f"/products/{product_id}")
    assert del_res.status_code == 200

    # Ensure it is deleted
    get_res = client.get(f"/products/{product_id}")
    assert get_res.status_code == 404


def test_product_not_found(client):
    """Test 404 response for nonexistent product."""
    res = client.get("/products/9999")
    assert res.status_code == 404

