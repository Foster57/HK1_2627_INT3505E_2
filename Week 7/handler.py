products = [
    {"id": 1, "name": "Laptop", "price": 1500.0},
    {"id": 2, "name": "Mouse", "price": 25.0},
]
next_id = 3


def get_products():
    return products, 200


def get_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product is None:
        return {"error": "Product not found"}, 404
    return product, 200


def create_product(body):
    global next_id
    product = {"id": next_id, **body}
    products.append(product)
    next_id += 1
    return product, 201


