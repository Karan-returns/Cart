import uuid
from decimal import Decimal

from store.domain import Order, OrderLineItem, utc_now
from store.exceptions import CartEmptyError
from store.repositories.cart_repo import CartRepository
from store.repositories.order_repo import OrderRepository
from store.repositories.product_repo import ProductRepository
from store.services.cart_service import CartService
from store.services.discount_service import DiscountService
from store.services.order_format import serialize_order


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

    def _build_line_items(self, customer_id: str) -> tuple[list[OrderLineItem], Decimal]:
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

        return line_items, subtotal

    def _apply_discount(
        self, subtotal: Decimal, discount_code: str | None
    ) -> tuple[Decimal, str | None, int | None]:
        if not discount_code:
            return Decimal("0.00"), None, None

        discount = self.discount_service.apply_code(discount_code)
        discount_amount = (subtotal * Decimal(discount.percent) / Decimal("100")).quantize(
            Decimal("0.01")
        )
        return discount_amount, discount.code, discount.percent

    def preview_checkout(self, customer_id: str, discount_code: str | None = None) -> dict:
        _, subtotal = self._build_line_items(customer_id)
        discount_amount, applied_code, discount_percent = self._apply_discount(
            subtotal, discount_code
        )
        total = subtotal - discount_amount

        return {
            "subtotal": str(subtotal),
            "discount_amount": str(discount_amount),
            "total": str(total),
            "discount_code": applied_code,
            "discount_percent": discount_percent,
            "discount_applied": applied_code is not None,
        }

    def checkout(self, customer_id: str, discount_code: str | None = None) -> dict:
        line_items, subtotal = self._build_line_items(customer_id)
        discount_amount, applied_code, _ = self._apply_discount(subtotal, discount_code)
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

        newly_issued = self.discount_service.generate_code(customer_id=customer_id)

        return {
            "order": serialize_order(order),
            "newly_issued_discount_code": (
                self._serialize_discount(newly_issued) if newly_issued else None
            ),
        }

    def _serialize_discount(self, discount) -> dict:
        return {
            "code": discount.code,
            "percent": discount.percent,
            "issued_for_order_number": discount.issued_for_order_number,
        }
