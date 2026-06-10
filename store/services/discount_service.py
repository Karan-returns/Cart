import secrets

from store.domain import DiscountCode
from store.exceptions import InvalidDiscountCodeError
from store.repositories.discount_repo import DiscountRepository
from store.repositories.order_repo import OrderRepository
from store.repositories.settings_repo import SettingsRepository


class DiscountService:
    def __init__(
        self,
        discount_repo: DiscountRepository | None = None,
        order_repo: OrderRepository | None = None,
        settings_repo: SettingsRepository | None = None,
    ):
        self.discount_repo = discount_repo or DiscountRepository()
        self.order_repo = order_repo or OrderRepository()
        self.settings_repo = settings_repo or SettingsRepository()

    @property
    def every_n_orders(self) -> int:
        return self.settings_repo.get().discount_every_n_orders

    @property
    def discount_percent(self) -> int:
        return self.settings_repo.get().discount_percent

    @property
    def code_prefix(self) -> str:
        return self.settings_repo.get().discount_code_prefix

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
        return f"{self.code_prefix}-{order_number}-{suffix}"

    def _customer_for_milestone_order(self, order_number: int) -> str | None:
        if order_number <= 0:
            return None
        orders = self.order_repo.list_all()
        if len(orders) < order_number:
            return None
        return orders[order_number - 1].customer_id

    def _owner_customer_id(self, code: DiscountCode) -> str | None:
        if code.issued_to_customer_id:
            return code.issued_to_customer_id
        return self._customer_for_milestone_order(code.issued_for_order_number)

    def list_available_for_customer(self, customer_id: str) -> list[DiscountCode]:
        available: list[DiscountCode] = []
        for code in self.discount_repo.list_all():
            if code.used:
                continue
            if self._owner_customer_id(code) == customer_id:
                available.append(code)
        available.sort(key=lambda c: c.created_at)
        return available

    def orders_until_next_reward(self) -> int:
        count = self.order_repo.completed_count()
        if count == 0:
            return self.every_n_orders
        remainder = count % self.every_n_orders
        return 0 if remainder == 0 else self.every_n_orders - remainder

    def generate_code(
        self, *, force: bool = False, customer_id: str | None = None
    ) -> DiscountCode | None:
        """
        Generate a discount code when the nth-order milestone is reached.
        Idempotent at milestones: returns existing unused code for the current
        milestone. When force=True (admin), always generates a new code; at a
        milestone, still returns an existing unused code if one exists.
        """
        order_number = self.order_repo.completed_count()
        at_milestone = (
            order_number > 0 and order_number % self.every_n_orders == 0
        )

        if not at_milestone and not force:
            return None

        if at_milestone:
            existing = self.discount_repo.find_unused_for_order_number(order_number)
            if existing:
                if customer_id and not existing.issued_to_customer_id:
                    existing.issued_to_customer_id = customer_id
                    return self.discount_repo.save(existing)
                return existing

        code = DiscountCode(
            code=self._generate_code_string(order_number),
            percent=self.discount_percent,
            issued_for_order_number=order_number,
            issued_to_customer_id=customer_id,
        )
        return self.discount_repo.save(code)

    def apply_code(self, code: str) -> DiscountCode:
        return self.validate_code(code)

    def mark_used(self, code: str) -> DiscountCode:
        return self.discount_repo.mark_used(code)
