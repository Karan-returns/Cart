from decimal import Decimal

from store.repositories.discount_repo import DiscountRepository
from store.repositories.order_repo import OrderRepository


class StatsService:
    def __init__(
        self,
        order_repo: OrderRepository | None = None,
        discount_repo: DiscountRepository | None = None,
    ):
        self.order_repo = order_repo or OrderRepository()
        self.discount_repo = discount_repo or DiscountRepository()

    def get_stats(self) -> dict:
        orders = self.order_repo.list_all()
        discounts = self.discount_repo.list_all()

        items_purchased = sum(
            item.quantity for order in orders for item in order.items
        )
        revenue = sum((order.total for order in orders), Decimal("0.00"))
        total_discounts_given = sum(
            (order.discount_amount for order in orders), Decimal("0.00")
        )

        return {
            "items_purchased": items_purchased,
            "revenue": str(revenue.quantize(Decimal("0.01"))),
            "discount_codes_issued": len(discounts),
            "discount_codes_used": sum(1 for d in discounts if d.used),
            "total_discounts_given": str(total_discounts_given.quantize(Decimal("0.01"))),
        }
