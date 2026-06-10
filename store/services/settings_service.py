from store.exceptions import StoreError
from store.repositories.settings_repo import SettingsRepository


class SettingsService:
    def __init__(self, settings_repo: SettingsRepository | None = None):
        self.settings_repo = settings_repo or SettingsRepository()

    def get_settings(self) -> dict:
        s = self.settings_repo.get()
        return {
            "discount_every_n_orders": s.discount_every_n_orders,
            "discount_percent": s.discount_percent,
            "discount_code_prefix": s.discount_code_prefix,
        }

    def update_settings(
        self,
        discount_every_n_orders: int | None = None,
        discount_percent: int | None = None,
        discount_code_prefix: str | None = None,
    ) -> dict:
        if discount_every_n_orders is not None and discount_every_n_orders < 1:
            raise StoreError("discount_every_n_orders must be at least 1.")
        if discount_percent is not None and not (1 <= discount_percent <= 100):
            raise StoreError("discount_percent must be between 1 and 100.")
        if discount_code_prefix is not None and not discount_code_prefix.strip():
            raise StoreError("discount_code_prefix cannot be empty.")

        updated = self.settings_repo.update(
            discount_every_n_orders=discount_every_n_orders,
            discount_percent=discount_percent,
            discount_code_prefix=discount_code_prefix.strip() if discount_code_prefix else None,
        )
        return {
            "discount_every_n_orders": updated.discount_every_n_orders,
            "discount_percent": updated.discount_percent,
            "discount_code_prefix": updated.discount_code_prefix,
        }
