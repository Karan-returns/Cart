from decimal import Decimal

from store.domain import (
    Cart,
    CartItem,
    DiscountCode,
    Order,
    OrderLineItem,
    Product,
    utc_now,
)


def product_to_doc(product: Product) -> dict:
    return {"_id": product.id, "name": product.name, "price": str(product.price)}


def product_from_doc(doc: dict) -> Product:
    return Product(id=doc["_id"], name=doc["name"], price=Decimal(doc["price"]))


def cart_to_doc(cart: Cart) -> dict:
    return {
        "_id": cart.customer_id,
        "items": [
            {"product_id": item.product_id, "quantity": item.quantity}
            for item in cart.items
        ],
    }


def cart_from_doc(doc: dict) -> Cart:
    return Cart(
        customer_id=doc["_id"],
        items=[
            CartItem(product_id=item["product_id"], quantity=item["quantity"])
            for item in doc.get("items", [])
        ],
    )


def order_to_doc(order: Order) -> dict:
    return {
        "_id": order.id,
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
        "created_at": order.created_at,
    }


def order_from_doc(doc: dict) -> Order:
    return Order(
        id=doc["_id"],
        customer_id=doc["customer_id"],
        items=[
            OrderLineItem(
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=Decimal(item["unit_price"]),
                line_total=Decimal(item["line_total"]),
            )
            for item in doc["items"]
        ],
        subtotal=Decimal(doc["subtotal"]),
        discount_amount=Decimal(doc["discount_amount"]),
        total=Decimal(doc["total"]),
        discount_code=doc.get("discount_code"),
        created_at=doc["created_at"],
    )


def discount_to_doc(code: DiscountCode) -> dict:
    doc = {
        "_id": code.code,
        "percent": code.percent,
        "issued_for_order_number": code.issued_for_order_number,
        "used": code.used,
        "created_at": code.created_at,
    }
    if code.issued_to_customer_id is not None:
        doc["issued_to_customer_id"] = code.issued_to_customer_id
    return doc


def discount_from_doc(doc: dict) -> DiscountCode:
    return DiscountCode(
        code=doc["_id"],
        percent=doc["percent"],
        issued_for_order_number=doc["issued_for_order_number"],
        issued_to_customer_id=doc.get("issued_to_customer_id"),
        used=doc.get("used", False),
        created_at=doc.get("created_at", utc_now()),
    )
