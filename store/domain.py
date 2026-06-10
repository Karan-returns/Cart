from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Product:
    id: str
    name: str
    price: Decimal


@dataclass
class CartItem:
    product_id: str
    quantity: int


@dataclass
class Cart:
    customer_id: str
    items: list[CartItem] = field(default_factory=list)


@dataclass
class OrderLineItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


@dataclass
class Order:
    id: str
    customer_id: str
    items: list[OrderLineItem]
    subtotal: Decimal
    discount_amount: Decimal
    total: Decimal
    discount_code: Optional[str]
    created_at: datetime


@dataclass
class DiscountCode:
    code: str
    percent: int
    issued_for_order_number: int
    used: bool = False
    created_at: datetime = field(default_factory=utc_now)
