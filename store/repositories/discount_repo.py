from store.domain import DiscountCode
from store.repositories.memory_store import get_store


class DiscountRepository:
    def save(self, code: DiscountCode) -> DiscountCode:
        store = get_store()
        with store.data_lock:
            store.discount_codes[code.code] = code
            return code

    def get(self, code: str) -> DiscountCode | None:
        store = get_store()
        with store.data_lock:
            return store.discount_codes.get(code)

    def list_all(self) -> list[DiscountCode]:
        store = get_store()
        with store.data_lock:
            return list(store.discount_codes.values())

    def find_unused_for_order_number(self, order_number: int) -> DiscountCode | None:
        store = get_store()
        with store.data_lock:
            for code in store.discount_codes.values():
                if code.issued_for_order_number == order_number and not code.used:
                    return code
            return None

    def mark_used(self, code: str) -> DiscountCode:
        store = get_store()
        with store.data_lock:
            discount = store.discount_codes[code]
            discount.used = True
            return discount
