from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"

    def ready(self):
        from store.repositories.mongo import ensure_indexes
        from store.repositories.product_repo import seed_products

        ensure_indexes()
        seed_products()
