from decimal import Decimal

from store.repositories.order_repo import OrderRepository
from store.repositories.settings_repo import SettingsRepository
from store.services.discount_service import DiscountService
from store.services.order_format import serialize_order


class CustomerService:
    def __init__(
        self,
        order_repo: OrderRepository | None = None,
        discount_service: DiscountService | None = None,
        settings_repo: SettingsRepository | None = None,
    ):
        self.order_repo = order_repo or OrderRepository()
        self.discount_service = discount_service or DiscountService(
            order_repo=self.order_repo
        )
        self.settings_repo = settings_repo or SettingsRepository()

    def _summarize_orders(self, orders: list) -> dict:
        items_purchased = sum(item.quantity for order in orders for item in order.items)
        total_spent = sum((order.total for order in orders), Decimal("0.00"))
        last_order_at = max((o.created_at for o in orders), default=None)

        return {
            "order_count": len(orders),
            "items_purchased": items_purchased,
            "total_spent": str(total_spent.quantize(Decimal("0.01"))),
            "last_order_at": last_order_at.isoformat() if last_order_at else None,
        }

    def _serialize_discount_code(self, code) -> dict:
        return {
            "code": code.code,
            "percent": code.percent,
            "issued_for_order_number": code.issued_for_order_number,
        }

    def get_profile(self, customer_id: str) -> dict:
        orders = self.order_repo.list_by_customer(customer_id)
        summary = self._summarize_orders(orders)
        settings = self.settings_repo.get()
        store_completed_orders = self.order_repo.completed_count()
        return {
            "customer_id": customer_id,
            **summary,
            "orders": [serialize_order(o) for o in orders],
            "store_completed_orders": store_completed_orders,
            "discount_every_n_orders": settings.discount_every_n_orders,
            "orders_until_next_reward": self.discount_service.orders_until_next_reward(),
            "available_discount_codes": [
                self._serialize_discount_code(code)
                for code in self.discount_service.list_available_for_customer(
                    customer_id
                )
            ],
        }

    def list_customers(self) -> dict:
        customers = []
        for customer_id in self.order_repo.list_customer_ids():
            orders = self.order_repo.list_by_customer(customer_id)
            customers.append(
                {
                    "customer_id": customer_id,
                    **self._summarize_orders(orders),
                }
            )
        customers.sort(key=lambda c: c.get("last_order_at") or "", reverse=True)
        return {"customers": customers, "total_customers": len(customers)}

    def get_customer_detail(self, customer_id: str) -> dict:
        return self.get_profile(customer_id)
