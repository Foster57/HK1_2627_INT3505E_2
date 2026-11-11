# Product API

Production-ready REST API for Products and Orders built with Flask, flask-smorest, Marshmallow, and SQLAlchemy.

## Cấu trúc thư mục

```
product-api/
├── pyproject.toml
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── gunicorn.conf.py
├── wsgi.py
├── migrations/
├── src/product_api/
│   ├── factory.py, config.py, extensions.py, errors.py
│   ├── api/ (products.py, orders.py, health.py, schemas.py)
│   └── models/ (product.py, order.py)
└── tests/
    ├── conftest.py
    ├── test_products.py
    └── test_orders.py
```

## Hướng dẫn cài đặt và chạy

### 1. Chạy trực tiếp với Python
```bash
# Di chuyển vào thư mục project
cd "Week 7/product-api"

# Copy file biến môi trường
cp .env.example .env

# Chạy server
python wsgi.py
```

API sẽ khởi chạy tại: `http://localhost:5000`
- Swagger UI Documentation: `http://localhost:5000/docs`
- OpenAPI JSON Spec: `http://localhost:5000/openapi.json`
- Health check: `http://localhost:5000/health/`

### 2. Chạy kiểm thử (Unit Tests)
```bash
pytest
```

### 3. Chạy với Docker & Docker Compose
```bash
docker compose up --build
```

