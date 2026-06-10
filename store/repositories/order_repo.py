from pymongo import ReturnDocument

from store.domain import Order
from store.repositories.mappers import order_from_doc, order_to_doc
from store.repositories.mongo import orders_collection, store_meta_collection


class OrderRepository:
    def create(self, order: Order) -> Order:
        orders_collection().insert_one(order_to_doc(order))
        store_meta_collection().find_one_and_update(
            {"_id": "global"},
            {"$inc": {"completed_order_count": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return order

    def list_all(self) -> list[Order]:
        return [
            order_from_doc(doc)
            for doc in orders_collection().find().sort("created_at", 1)
        ]

    def completed_count(self) -> int:
        doc = store_meta_collection().find_one({"_id": "global"})
        return doc.get("completed_order_count", 0) if doc else 0

    def list_by_customer(self, customer_id: str) -> list[Order]:
        return [
            order_from_doc(doc)
            for doc in orders_collection()
            .find({"customer_id": customer_id})
            .sort("created_at", 1)
        ]

    def list_customer_ids(self) -> list[str]:
        return orders_collection().distinct("customer_id")
