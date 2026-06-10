from store.domain import Cart
from store.repositories.mappers import cart_from_doc, cart_to_doc
from store.repositories.mongo import carts_collection


class CartRepository:
    def get(self, customer_id: str) -> Cart:
        doc = carts_collection().find_one({"_id": customer_id})
        if doc is None:
            return Cart(customer_id=customer_id)
        return cart_from_doc(doc)

    def save(self, cart: Cart) -> Cart:
        carts_collection().replace_one(
            {"_id": cart.customer_id},
            cart_to_doc(cart),
            upsert=True,
        )
        return cart

    def clear(self, customer_id: str) -> None:
        carts_collection().delete_one({"_id": customer_id})
