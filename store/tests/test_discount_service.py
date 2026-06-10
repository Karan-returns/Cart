import uuid
from decimal import Decimal

from store.domain import Order, OrderLineItem, utc_now
from store.exceptions import InvalidDiscountCodeError
from store.repositories.discount_repo import DiscountRepository
from store.repositories.order_repo import OrderRepository
from store.services.discount_service import DiscountService
from store.tests.base import StoreTestCase


class DiscountServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.discount_repo = DiscountRepository()
        self.order_repo = OrderRepository()
        self.service = DiscountService(
            discount_repo=self.discount_repo,
            order_repo=self.order_repo,
        )

    def _create_order(self, customer_id: str = "alice"):
        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            items=[
                OrderLineItem(
                    product_id="prod-1",
                    product_name="Wireless Mouse",
                    quantity=1,
                    unit_price=Decimal("29.99"),
                    line_total=Decimal("29.99"),
                )
            ],
            subtotal=Decimal("29.99"),
            discount_amount=Decimal("0.00"),
            total=Decimal("29.99"),
            discount_code=None,
            created_at=utc_now(),
        )
        self.order_repo.create(order)

    def test_no_generation_before_milestone(self):
        self._create_order()
        self._create_order()
        result = self.service.generate_code()
        self.assertIsNone(result)

    def test_auto_generate_on_nth_order(self):
        for _ in range(3):
            self._create_order()
        code = self.service.generate_code()
        self.assertIsNotNone(code)
        self.assertEqual(code.percent, 10)
        self.assertTrue(code.code.startswith("SAVE-3-"))

    def test_idempotent_generation(self):
        for _ in range(3):
            self._create_order()
        first = self.service.generate_code()
        second = self.service.generate_code()
        self.assertEqual(first.code, second.code)

    def test_validate_and_reject_used_code(self):
        for _ in range(3):
            self._create_order()
        code = self.service.generate_code()
        self.discount_repo.mark_used(code.code)
        with self.assertRaises(InvalidDiscountCodeError):
            self.service.validate_code(code.code)

    def test_admin_force_generates_between_milestones(self):
        self._create_order()
        self._create_order()
        code = self.service.generate_code(force=True)
        self.assertIsNotNone(code)
        self.assertEqual(code.percent, 10)
        self.assertTrue(code.code.startswith("SAVE-2-"))
        self.assertEqual(code.issued_for_order_number, 2)

    def test_admin_force_succeeds_at_milestone(self):
        for _ in range(3):
            self._create_order()
        code = self.service.generate_code(force=True)
        self.assertIsNotNone(code)

    def test_milestone_code_assigned_to_checkout_customer(self):
        for customer in ("u1", "u2"):
            self._create_order(customer_id=customer)
        self._create_order(customer_id="u3")
        code = self.service.generate_code(customer_id="u3")
        self.assertIsNotNone(code)
        self.assertEqual(code.issued_to_customer_id, "u3")

    def test_list_available_for_customer_infers_owner_from_orders(self):
        for customer in ("u1", "u2", "u3"):
            self._create_order(customer_id=customer)
        code = self.service.generate_code()
        self.assertIsNotNone(code)

        available = self.service.list_available_for_customer("u3")
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].code, code.code)

        self.assertEqual(self.service.list_available_for_customer("u1"), [])
