from flask.views import MethodView
from flask_smorest import Blueprint, abort
from product_api.api.schemas import (
    MessageSchema,
    ProductCreateSchema,
    ProductSchema,
    ProductUpdateSchema,
)
from product_api.extensions import db
from product_api.models import Product

blp = Blueprint("products", __name__, url_prefix="/products", description="Product operations")


@blp.route("/")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """List all products"""
        return db.session.query(Product).order_by(Product.id.asc()).all()

    @blp.arguments(ProductCreateSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        """Create a new product"""
        product = Product(
            name=data["name"],
            price=data["price"],
            description=data.get("description", ""),
            stock=data.get("stock", 0),
        )
        db.session.add(product)
        db.session.commit()
        return product


@blp.route("/<int:product_id>")
class ProductItem(MethodView):
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        """Get a single product by ID"""
        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            abort(404, message="Product not found")
        return product

    @blp.arguments(ProductUpdateSchema)
    @blp.response(200, ProductSchema)
    def put(self, data, product_id):
        """Update a product by ID"""
        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            abort(404, message="Product not found")

        for key, value in data.items():
            if value is not None:
                setattr(product, key, value)

        db.session.commit()
        return product

    @blp.response(200, MessageSchema)
    def delete(self, product_id):
        """Delete a product by ID"""
        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            abort(404, message="Product not found")

        db.session.delete(product)
        db.session.commit()
        return {"message": f"Product {product_id} deleted successfully", "status_code": 200}

