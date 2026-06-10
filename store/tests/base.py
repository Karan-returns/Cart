from django.test import TestCase, override_settings

from store.repositories.memory_store import get_store
from store.repositories.product_repo import seed_products


@override_settings(
    DISCOUNT_EVERY_N_ORDERS=3,
    DISCOUNT_PERCENT=10,
    DISCOUNT_CODE_PREFIX="SAVE",
    ADMIN_API_KEY="test-admin-key",
)
class StoreTestCase(TestCase):
    def setUp(self):
        super().setUp()
        get_store().reset()
        seed_products()
