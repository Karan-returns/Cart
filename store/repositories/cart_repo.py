from store.domain import Cart, CartItem
from store.repositories.memory_store import get_store


class CartRepository:
    def get(self, customer_id: str) -> Cart:
        store = get_store()
        with store.data_lock:
            if customer_id not in store.carts:
                store.carts[customer_id] = Cart(customer_id=customer_id)
            return store.carts[customer_id]

    def save(self, cart: Cart) -> Cart:
        store = get_store()
        with store.data_lock:
            store.carts[cart.customer_id] = cart
            return cart

    def clear(self, customer_id: str) -> None:
        store = get_store()
        with store.data_lock:
            store.carts.pop(customer_id, None)
