from decimal import Decimal

from store.domain import Product
from store.repositories.memory_store import get_store

DEFAULT_PRODUCTS = [
    Product(id="prod-1", name="Wireless Mouse", price=Decimal("29.99")),
    Product(id="prod-2", name="Mechanical Keyboard", price=Decimal("89.99")),
    Product(id="prod-3", name="USB-C Hub", price=Decimal("49.99")),
    Product(id="prod-4", name="Laptop Stand", price=Decimal("39.99")),
    Product(id="prod-5", name="Webcam HD", price=Decimal("59.99")),
]


def seed_products():
    store = get_store()
    with store.data_lock:
        if store.products:
            return
        for product in DEFAULT_PRODUCTS:
            store.products[product.id] = product


class ProductRepository:
    def list_all(self) -> list[Product]:
        store = get_store()
        with store.data_lock:
            return list(store.products.values())

    def get(self, product_id: str) -> Product | None:
        store = get_store()
        with store.data_lock:
            return store.products.get(product_id)
