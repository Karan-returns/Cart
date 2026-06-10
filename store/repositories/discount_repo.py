from store.domain import DiscountCode
from store.repositories.mappers import discount_from_doc, discount_to_doc
from store.repositories.mongo import discount_codes_collection


class DiscountRepository:
    def save(self, code: DiscountCode) -> DiscountCode:
        discount_codes_collection().replace_one(
            {"_id": code.code},
            discount_to_doc(code),
            upsert=True,
        )
        return code

    def get(self, code: str) -> DiscountCode | None:
        doc = discount_codes_collection().find_one({"_id": code})
        return discount_from_doc(doc) if doc else None

    def list_all(self) -> list[DiscountCode]:
        return [
            discount_from_doc(doc) for doc in discount_codes_collection().find()
        ]

    def find_unused_for_order_number(self, order_number: int) -> DiscountCode | None:
        doc = discount_codes_collection().find_one(
            {"issued_for_order_number": order_number, "used": False}
        )
        return discount_from_doc(doc) if doc else None

    def mark_used(self, code: str) -> DiscountCode:
        discount_codes_collection().update_one(
            {"_id": code},
            {"$set": {"used": True}},
        )
        doc = discount_codes_collection().find_one({"_id": code})
        return discount_from_doc(doc)
