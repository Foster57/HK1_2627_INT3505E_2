from marshmallow import Schema, fields, validate


class ProductCreateSchema(Schema):
    """Schema for creating a product."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    description = fields.Str(load_default="", validate=validate.Length(max=255))
    stock = fields.Int(load_default=0, validate=validate.Range(min=0))


class ProductUpdateSchema(Schema):
    """Schema for updating a product."""

    name = fields.Str(validate=validate.Length(min=1, max=100))
    price = fields.Float(validate=validate.Range(min=0))
    description = fields.Str(validate=validate.Length(max=255))
    stock = fields.Int(validate=validate.Range(min=0))


class ProductSchema(ProductCreateSchema):
    """Schema for serializing a product."""

    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class OrderItemCreateSchema(Schema):
    """Schema for item in order creation."""

    product_id = fields.Int(required=True)
    quantity = fields.Int(load_default=1, validate=validate.Range(min=1))


class OrderItemSchema(Schema):
    """Schema for serializing an order item."""

    id = fields.Int(dump_only=True)
    product_id = fields.Int(dump_only=True)
    product_name = fields.Str(dump_only=True)
    quantity = fields.Int(dump_only=True)
    unit_price = fields.Float(dump_only=True)
    subtotal = fields.Float(dump_only=True)


class OrderCreateSchema(Schema):
    """Schema for creating an order."""

    customer_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    items = fields.List(
        fields.Nested(OrderItemCreateSchema),
        required=True,
        validate=validate.Length(min=1),
    )


class OrderStatusUpdateSchema(Schema):
    """Schema for updating order status."""

    status = fields.Str(
        required=True,
        validate=validate.OneOf(["pending", "processing", "completed", "cancelled"]),
    )


class OrderSchema(Schema):
    """Schema for serializing an order."""

    id = fields.Int(dump_only=True)
    customer_name = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    total_price = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema), dump_only=True)


class HealthSchema(Schema):
    """Schema for health status check."""

    status = fields.Str(dump_only=True)
    version = fields.Str(dump_only=True)
    database = fields.Str(dump_only=True)


class MessageSchema(Schema):
    """Standard message response schema."""

    message = fields.Str(dump_only=True)
    status_code = fields.Int(dump_only=True)

