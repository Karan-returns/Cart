from store.exceptions import InvalidQuantityError, ProductNotFoundError
from store.services.cart_service import CartService
from store.tests.base import StoreTestCase


class CartServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.service = CartService()

    def test_add_item_to_cart(self):
        cart = self.service.add_item("alice", "prod-1", 2)
        self.assertEqual(len(cart.items), 1)
        self.assertEqual(cart.items[0].quantity, 2)

    def test_merge_quantities_for_same_product(self):
        self.service.add_item("alice", "prod-1", 2)
        cart = self.service.add_item("alice", "prod-1", 3)
        self.assertEqual(len(cart.items), 1)
        self.assertEqual(cart.items[0].quantity, 5)

    def test_reject_invalid_quantity(self):
        with self.assertRaises(InvalidQuantityError):
            self.service.add_item("alice", "prod-1", 0)

    def test_reject_unknown_product(self):
        with self.assertRaises(ProductNotFoundError):
            self.service.add_item("alice", "unknown", 1)

    def test_get_cart_with_totals(self):
        self.service.add_item("alice", "prod-1", 2)
        cart = self.service.get_cart("alice")
        self.assertEqual(cart["customer_id"], "alice")
        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(cart["subtotal"], "59.98")
