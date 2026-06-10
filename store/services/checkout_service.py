import uuid
from decimal import Decimal

from store.domain import Order, OrderLineItem, utc_now
from store.exceptions import CartEmptyError
from store.repositories.cart_repo import CartRepository
from store.repositories.order_repo import OrderRepository
from store.repositories.product_repo import ProductRepository
from store.services.cart_service import CartService
from store.services.discount_service import DiscountService


class CheckoutService:
    def __init__(
        self,
        cart_repo: CartRepository | None = None,
        order_repo: OrderRepository | None = None,
        product_repo: ProductRepository | None = None,
        cart_service: CartService | None = None,
        discount_service: DiscountService | None = None,
    ):
        self.cart_repo = cart_repo or CartRepository()
        self.order_repo = order_repo or OrderRepository()
        self.product_repo = product_repo or ProductRepository()
        self.cart_service = cart_service or CartService(
            cart_repo=self.cart_repo, product_repo=self.product_repo
        )
        self.discount_service = discount_service or DiscountService(
            order_repo=self.order_repo
        )

    def checkout(self, customer_id: str, discount_code: str | None = None) -> dict:
        cart = self.cart_repo.get(customer_id)
        if not cart.items:
            raise CartEmptyError()

        line_items: list[OrderLineItem] = []
        subtotal = Decimal("0.00")

        for item in cart.items:
            product = self.product_repo.get(item.product_id)
            if product is None:
                continue
            line_total = product.price * item.quantity
            subtotal += line_total
            line_items.append(
                OrderLineItem(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item.quantity,
                    unit_price=product.price,
                    line_total=line_total,
                )
            )

        if not line_items:
            raise CartEmptyError()

        discount_amount = Decimal("0.00")
        applied_code = None

        if discount_code:
            discount = self.discount_service.apply_code(discount_code)
            discount_amount = (subtotal * Decimal(discount.percent) / Decimal("100")).quantize(
                Decimal("0.01")
            )
            applied_code = discount.code

        total = subtotal - discount_amount

        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            items=line_items,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total,
            discount_code=applied_code,
            created_at=utc_now(),
        )
        self.order_repo.create(order)

        if applied_code:
            self.discount_service.mark_used(applied_code)

        self.cart_repo.clear(customer_id)

        newly_issued = self.discount_service.generate_code()

        return {
            "order": self._serialize_order(order),
            "newly_issued_discount_code": (
                self._serialize_discount(newly_issued) if newly_issued else None
            ),
        }

    def _serialize_order(self, order: Order) -> dict:
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

    def _serialize_discount(self, discount) -> dict:
        return {
            "code": discount.code,
            "percent": discount.percent,
            "issued_for_order_number": discount.issued_for_order_number,
        }
