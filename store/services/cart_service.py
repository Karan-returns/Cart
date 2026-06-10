from decimal import Decimal

from store.domain import Cart, CartItem, Product
from store.exceptions import InvalidQuantityError, ProductNotFoundError
from store.repositories.cart_repo import CartRepository
from store.repositories.product_repo import ProductRepository


class CartService:
    def __init__(
        self,
        cart_repo: CartRepository | None = None,
        product_repo: ProductRepository | None = None,
    ):
        self.cart_repo = cart_repo or CartRepository()
        self.product_repo = product_repo or ProductRepository()

    def add_item(self, customer_id: str, product_id: str, quantity: int) -> Cart:
        if quantity <= 0:
            raise InvalidQuantityError()

        product = self.product_repo.get(product_id)
        if product is None:
            raise ProductNotFoundError()

        cart = self.cart_repo.get(customer_id)
        for item in cart.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return self.cart_repo.save(cart)

        cart.items.append(CartItem(product_id=product_id, quantity=quantity))
        return self.cart_repo.save(cart)

    def get_cart(self, customer_id: str) -> dict:
        cart = self.cart_repo.get(customer_id)
        line_items = []
        subtotal = Decimal("0.00")

        for item in cart.items:
            product = self.product_repo.get(item.product_id)
            if product is None:
                continue
            line_total = product.price * item.quantity
            subtotal += line_total
            line_items.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "unit_price": str(product.price),
                    "line_total": str(line_total),
                }
            )

        return {
            "customer_id": customer_id,
            "items": line_items,
            "subtotal": str(subtotal),
        }

    def get_product(self, product_id: str) -> Product:
        product = self.product_repo.get(product_id)
        if product is None:
            raise ProductNotFoundError()
        return product
