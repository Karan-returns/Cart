import threading
from typing import Any


class MemoryStore:
    """Thread-safe singleton in-memory store for carts, orders, and discounts."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_store()
        return cls._instance

    def _init_store(self):
        self.data_lock = threading.Lock()
        self.products: dict[str, Any] = {}
        self.carts: dict[str, Any] = {}
        self.orders: list[Any] = []
        self.discount_codes: dict[str, Any] = {}
        self.completed_order_count: int = 0
        self._order_counter: int = 0

    def reset(self):
        """Reset all state — used in tests."""
        with self.data_lock:
            self.products.clear()
            self.carts.clear()
            self.orders.clear()
            self.discount_codes.clear()
            self.completed_order_count = 0
            self._order_counter = 0


def get_store() -> MemoryStore:
    return MemoryStore()
