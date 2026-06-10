from store.repositories.order_repo import OrderRepository
from store.services.cart_service import CartService
from store.services.checkout_service import CheckoutService
from store.services.customer_service import CustomerService
from store.tests.base import StoreTestCase


class CustomerServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.order_repo = OrderRepository()
        self.service = CustomerService(order_repo=self.order_repo)
        self.cart_service = CartService()
        self.checkout_service = CheckoutService()

    def test_profile_for_customer_with_no_orders(self):
        profile = self.service.get_profile("new-user")
        self.assertEqual(profile["order_count"], 0)
        self.assertEqual(profile["orders"], [])

    def test_profile_after_checkout(self):
        self.cart_service.add_item("alice", "prod-1", 2)
        self.checkout_service.checkout("alice")

        profile = self.service.get_profile("alice")
        self.assertEqual(profile["order_count"], 1)
        self.assertEqual(profile["items_purchased"], 2)
        self.assertEqual(len(profile["orders"]), 1)
        self.assertEqual(profile["orders"][0]["items"][0]["product_name"], "Wireless Mouse")
        self.assertEqual(profile["store_completed_orders"], 1)
        self.assertEqual(profile["discount_every_n_orders"], 3)
        self.assertEqual(profile["orders_until_next_reward"], 2)
        self.assertEqual(profile["available_discount_codes"], [])

    def test_profile_includes_milestone_discount_code(self):
        for customer in ("u1", "u2", "u3"):
            self.cart_service.add_item(customer, "prod-1", 1)
            self.checkout_service.checkout(customer)

        profile = self.service.get_profile("u3")
        self.assertEqual(len(profile["available_discount_codes"]), 1)
        self.assertEqual(profile["available_discount_codes"][0]["percent"], 10)
        self.assertEqual(profile["orders_until_next_reward"], 3)

    def test_list_customers(self):
        self.cart_service.add_item("alice", "prod-1", 1)
        self.checkout_service.checkout("alice")
        self.cart_service.add_item("bob", "prod-2", 1)
        self.checkout_service.checkout("bob")

        result = self.service.list_customers()
        self.assertEqual(result["total_customers"], 2)
        ids = {c["customer_id"] for c in result["customers"]}
        self.assertEqual(ids, {"alice", "bob"})
