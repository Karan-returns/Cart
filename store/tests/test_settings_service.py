from store.exceptions import StoreError
from store.services.discount_service import DiscountService
from store.services.settings_service import SettingsService
from store.tests.base import StoreTestCase


class SettingsServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.service = SettingsService()

    def test_update_settings(self):
        result = self.service.update_settings(
            discount_every_n_orders=5,
            discount_percent=15,
            discount_code_prefix="DEAL",
        )
        self.assertEqual(result["discount_every_n_orders"], 5)
        self.assertEqual(result["discount_percent"], 15)
        self.assertEqual(result["discount_code_prefix"], "DEAL")

    def test_discount_service_uses_updated_settings(self):
        self.service.update_settings(discount_every_n_orders=2, discount_percent=20)
        discount_service = DiscountService()
        self.assertEqual(discount_service.every_n_orders, 2)
        self.assertEqual(discount_service.discount_percent, 20)

    def test_reject_invalid_percent(self):
        with self.assertRaises(StoreError):
            self.service.update_settings(discount_percent=0)
