from dataclasses import dataclass

from django.conf import settings as django_settings

from store.repositories.mongo import get_global_meta, store_meta_collection


@dataclass
class StoreSettings:
    discount_every_n_orders: int
    discount_percent: int
    discount_code_prefix: str


class SettingsRepository:
    def get(self) -> StoreSettings:
        meta = get_global_meta()
        overrides = meta.get("settings_overrides", {})
        return StoreSettings(
            discount_every_n_orders=overrides.get(
                "discount_every_n_orders", django_settings.DISCOUNT_EVERY_N_ORDERS
            ),
            discount_percent=overrides.get(
                "discount_percent", django_settings.DISCOUNT_PERCENT
            ),
            discount_code_prefix=overrides.get(
                "discount_code_prefix", django_settings.DISCOUNT_CODE_PREFIX
            ),
        )

    def update(self, **kwargs) -> StoreSettings:
        allowed = {"discount_every_n_orders", "discount_percent", "discount_code_prefix"}
        updates = {
            f"settings_overrides.{key}": value
            for key, value in kwargs.items()
            if key in allowed and value is not None
        }
        if updates:
            store_meta_collection().update_one(
                {"_id": "global"},
                {"$set": updates},
                upsert=True,
            )
        return self.get()
