from store.domain import Order


def serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "line_total": str(item.line_total),
            }
            for item in order.items
        ],
        "subtotal": str(order.subtotal),
        "discount_amount": str(order.discount_amount),
        "total": str(order.total),
        "discount_code": order.discount_code,
        "created_at": order.created_at.isoformat(),
    }
