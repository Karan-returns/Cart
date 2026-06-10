from store.domain import Order
from store.repositories.memory_store import get_store


class OrderRepository:
    def create(self, order: Order) -> Order:
        store = get_store()
        with store.data_lock:
            store._order_counter += 1
            store.orders.append(order)
            store.completed_order_count += 1
            return order

    def list_all(self) -> list[Order]:
        store = get_store()
        with store.data_lock:
            return list(store.orders)

    def completed_count(self) -> int:
        store = get_store()
        with store.data_lock:
            return store.completed_order_count
