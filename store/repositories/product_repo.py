from decimal import Decimal

from store.domain import Product
from store.repositories.mappers import product_from_doc, product_to_doc
from store.repositories.mongo import products_collection

DEFAULT_PRODUCTS = [
    Product(id="prod-1", name="Wireless Mouse", price=Decimal("29.99")),
    Product(id="prod-2", name="Mechanical Keyboard", price=Decimal("89.99")),
    Product(id="prod-3", name="USB-C Hub", price=Decimal("49.99")),
    Product(id="prod-4", name="Laptop Stand", price=Decimal("39.99")),
    Product(id="prod-5", name="Webcam HD", price=Decimal("59.99")),
]


def seed_products():
    col = products_collection()
    if col.count_documents({}) > 0:
        return
    col.insert_many([product_to_doc(p) for p in DEFAULT_PRODUCTS])


class ProductRepository:
    def list_all(self) -> list[Product]:
        return [product_from_doc(doc) for doc in products_collection().find()]

    def get(self, product_id: str) -> Product | None:
        doc = products_collection().find_one({"_id": product_id})
        return product_from_doc(doc) if doc else None
