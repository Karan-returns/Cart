from decimal import Decimal

from store.exceptions import CartEmptyError, InvalidDiscountCodeError
from store.repositories.cart_repo import CartRepository
from store.repositories.discount_repo import DiscountRepository
from store.repositories.order_repo import OrderRepository
from store.repositories.product_repo import ProductRepository
from store.services.cart_service import CartService
from store.services.checkout_service import CheckoutService
from store.services.discount_service import DiscountService
from store.tests.base import StoreTestCase


class CheckoutServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.cart_repo = CartRepository()
        self.order_repo = OrderRepository()
        self.product_repo = ProductRepository()
        self.discount_repo = DiscountRepository()
        self.cart_service = CartService(
            cart_repo=self.cart_repo,
            product_repo=self.product_repo,
        )
        self.discount_service = DiscountService(
            discount_repo=self.discount_repo,
            order_repo=self.order_repo,
        )
        self.service = CheckoutService(
            cart_repo=self.cart_repo,
            order_repo=self.order_repo,
            product_repo=self.product_repo,
            cart_service=self.cart_service,
            discount_service=self.discount_service,
        )

    def test_checkout_empty_cart_raises(self):
        with self.assertRaises(CartEmptyError):
            self.service.checkout("alice")

    def test_preview_checkout_with_discount(self):
        for customer in ("p1", "p2", "p3"):
            self.cart_service.add_item(customer, "prod-1", 1)
            self.service.checkout(customer)

        code = self.discount_service.generate_code()
        self.cart_service.add_item("alice", "prod-1", 1)
        preview = self.service.preview_checkout("alice", discount_code=code.code)
        self.assertTrue(preview["discount_applied"])
        self.assertEqual(preview["discount_amount"], "3.00")
        self.assertEqual(preview["total"], "26.99")

    def test_preview_checkout_invalid_discount_raises(self):
        self.cart_service.add_item("alice", "prod-1", 1)
        with self.assertRaises(InvalidDiscountCodeError):
            self.service.preview_checkout("alice", discount_code="BAD")

    def test_successful_checkout(self):
        self.cart_service.add_item("alice", "prod-1", 2)
        result = self.service.checkout("alice")
        self.assertEqual(result["order"]["subtotal"], "59.98")
        self.assertEqual(result["order"]["total"], "59.98")
        self.assertEqual(result["order"]["discount_amount"], "0.00")
        self.assertIsNone(result["newly_issued_discount_code"])

    def test_checkout_with_valid_discount(self):
        for customer in ("bob", "carol", "dave"):
            self.cart_service.add_item(customer, "prod-1", 1)
            self.service.checkout(customer)

        code = self.discount_service.generate_code()
        self.cart_service.add_item("alice", "prod-1", 1)
        result = self.service.checkout("alice", discount_code=code.code)
        self.assertEqual(result["order"]["discount_amount"], "3.00")
        self.assertEqual(result["order"]["total"], "26.99")

    def test_checkout_with_invalid_discount_raises(self):
        self.cart_service.add_item("alice", "prod-1", 1)
        with self.assertRaises(InvalidDiscountCodeError):
            self.service.checkout("alice", discount_code="INVALID")

    def test_auto_issue_discount_on_nth_order(self):
        for customer in ("u1", "u2"):
            self.cart_service.add_item(customer, "prod-1", 1)
            self.service.checkout(customer)

        self.cart_service.add_item("u3", "prod-1", 1)
        result = self.service.checkout("u3")
        self.assertIsNotNone(result["newly_issued_discount_code"])
        self.assertEqual(result["newly_issued_discount_code"]["percent"], 10)
