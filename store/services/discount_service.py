import secrets

from django.conf import settings

from store.domain import DiscountCode
from store.exceptions import DiscountGenerationError, InvalidDiscountCodeError
from store.repositories.discount_repo import DiscountRepository
from store.repositories.order_repo import OrderRepository


class DiscountService:
    def __init__(
        self,
        discount_repo: DiscountRepository | None = None,
        order_repo: OrderRepository | None = None,
    ):
        self.discount_repo = discount_repo or DiscountRepository()
        self.order_repo = order_repo or OrderRepository()

    @property
    def every_n_orders(self) -> int:
        return settings.DISCOUNT_EVERY_N_ORDERS

    @property
    def discount_percent(self) -> int:
        return settings.DISCOUNT_PERCENT

    def is_milestone_reached(self) -> bool:
        count = self.order_repo.completed_count()
        return count > 0 and count % self.every_n_orders == 0

    def validate_code(self, code: str) -> DiscountCode:
        discount = self.discount_repo.get(code)
        if discount is None or discount.used:
            raise InvalidDiscountCodeError()
        return discount

    def _generate_code_string(self, order_number: int) -> str:
        suffix = secrets.token_hex(3).upper()
        prefix = settings.DISCOUNT_CODE_PREFIX
        return f"{prefix}-{order_number}-{suffix}"

    def generate_code(self, *, force: bool = False) -> DiscountCode | None:
        """
        Generate a discount code when the nth-order milestone is reached.
        Idempotent: returns existing unused code for the current milestone.
        When force=True (admin override), raises if condition not met.
        """
        order_number = self.order_repo.completed_count()

        if order_number == 0 or order_number % self.every_n_orders != 0:
            if force:
                raise DiscountGenerationError(
                    f"Order count ({order_number}) has not reached a milestone "
                    f"(every {self.every_n_orders} orders)."
                )
            return None

        existing = self.discount_repo.find_unused_for_order_number(order_number)
        if existing:
            return existing

        code = DiscountCode(
            code=self._generate_code_string(order_number),
            percent=self.discount_percent,
            issued_for_order_number=order_number,
        )
        return self.discount_repo.save(code)

    def apply_code(self, code: str) -> DiscountCode:
        return self.validate_code(code)

    def mark_used(self, code: str) -> DiscountCode:
        return self.discount_repo.mark_used(code)
