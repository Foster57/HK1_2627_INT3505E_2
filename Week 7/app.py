from flask import redirect
from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields, validate

app = Flask(__name__)
app.config.update(
    API_TITLE="Products API",
    API_VERSION="v1",
    OPENAPI_VERSION="3.0.3",
    OPENAPI_URL_PREFIX="/",
    OPENAPI_JSON_PATH="openapi.json",
    OPENAPI_SWAGGER_UI_PATH="/docs",
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
)

api = Api(app)
blp = Blueprint("products", __name__, url_prefix="/products", description="Product operations")



class ProductCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))


class ProductSchema(ProductCreateSchema):
    id = fields.Int(dump_only=True)


# ---------- Data ----------
products = [
    {"id": 1, "name": "Laptop", "price": 1500.0},
    {"id": 2, "name": "Mouse", "price": 25.0},
]
next_id = 3


@blp.route("/")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """Lấy danh sách sản phẩm"""
        return products

    @blp.arguments(ProductCreateSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        """Thêm sản phẩm mới"""
        global next_id
        product = {"id": next_id, **data}
        products.append(product)
        next_id += 1
        return product


@blp.route("/<int:product_id>")
class ProductItem(MethodView):
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        """Lấy 1 sản phẩm theo id"""
        product = next((p for p in products if p["id"] == product_id), None)
        if product is None:
            abort(404, message="Product not found")
        return product


api.register_blueprint(blp)

@app.route("/")
def index():
    return redirect("/docs")


if __name__ == "__main__":
    app.run(debug=True)
