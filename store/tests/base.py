from django.test import TestCase, override_settings

from store.repositories.mongo import reset_client, reset_database
from store.repositories.product_repo import seed_products


@override_settings(
    DISCOUNT_EVERY_N_ORDERS=3,
    DISCOUNT_PERCENT=10,
    DISCOUNT_CODE_PREFIX="SAVE",
    ADMIN_API_KEY="test-admin-key",
    MONGODB_DB_NAME="cart_store_test",
    # Uses the same Atlas cluster as dev; tests wipe cart_store_test only.
    MONGODB_URI=__import__("os").environ.get(
        "MONGODB_URI", "mongodb://localhost:27017"
    ),
)
class StoreTestCase(TestCase):
    def setUp(self):
        super().setUp()
        reset_client()
        reset_database()
        seed_products()
