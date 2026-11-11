from flask.views import MethodView
from flask_smorest import Blueprint, abort
from product_api.api.schemas import (
    MessageSchema,
    OrderCreateSchema,
    OrderSchema,
    OrderStatusUpdateSchema,
)
from product_api.extensions import db
from product_api.models import Order, OrderItem, Product

blp = Blueprint("orders", __name__, url_prefix="/orders", description="Order operations")


@blp.route("/")
class OrderList(MethodView):
    @blp.response(200, OrderSchema(many=True))
    def get(self):
        """List all orders"""
        return db.session.query(Order).order_by(Order.id.desc()).all()

    @blp.arguments(OrderCreateSchema)
    @blp.response(201, OrderSchema)
    def post(self, data):
        """Create a new order"""
        customer_name = data["customer_name"]
        items_data = data["items"]

        if not items_data:
            abort(400, message="Order must contain at least one item")

        order = Order(customer_name=customer_name, status="pending", total_price=0.0)
        db.session.add(order)
        db.session.flush()

        total_price = 0.0
        for item_data in items_data:
            product = db.session.query(Product).filter_by(id=item_data["product_id"]).first()
            if not product:
                db.session.rollback()
                abort(404, message=f"Product with id {item_data['product_id']} not found")

            quantity = item_data.get("quantity", 1)
            unit_price = product.price
            subtotal = quantity * unit_price
            total_price += subtotal

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
            )
            db.session.add(order_item)

        order.total_price = round(total_price, 2)
        db.session.commit()
        return order


@blp.route("/<int:order_id>")
class OrderItemResource(MethodView):
    @blp.response(200, OrderSchema)
    def get(self, order_id):
        """Get an order by ID"""
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            abort(404, message="Order not found")
        return order

    @blp.response(200, MessageSchema)
    def delete(self, order_id):
        """Delete an order by ID"""
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            abort(404, message="Order not found")

        db.session.delete(order)
        db.session.commit()
        return {"message": f"Order {order_id} deleted successfully", "status_code": 200}


@blp.route("/<int:order_id>/status")
class OrderStatusResource(MethodView):
    @blp.arguments(OrderStatusUpdateSchema)
    @blp.response(200, OrderSchema)
    def patch(self, data, order_id):
        """Update order status"""
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            abort(404, message="Order not found")

        order.status = data["status"]
        db.session.commit()
        return order

