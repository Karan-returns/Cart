from django.conf import settings
from pymongo import ASCENDING, MongoClient

_client: MongoClient | None = None


def reset_client():
    """Close and clear the cached client (used in tests)."""
    global _client
    if _client is not None:
        _client.close()
    _client = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = settings.MONGODB_URI
        if not uri:
            raise ValueError(
                "MONGODB_URI is not set. Add your MongoDB Atlas connection string "
                "to .env (mongodb+srv://...). See README.md for setup steps."
            )
        _client = MongoClient(
            uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
        _client.admin.command("ping")
    return _client


def get_db():
    return get_client()[settings.MONGODB_DB_NAME]


def products_collection():
    return get_db()["products"]


def carts_collection():
    return get_db()["carts"]


def orders_collection():
    return get_db()["orders"]


def discount_codes_collection():
    return get_db()["discount_codes"]


def store_meta_collection():
    return get_db()["store_meta"]


def ensure_indexes():
    orders_collection().create_index([("customer_id", ASCENDING)])
    discount_codes_collection().create_index(
        [("issued_for_order_number", ASCENDING), ("used", ASCENDING)]
    )


def reset_database():
    """Drop all application data — used in tests."""
    db = get_db()
    for name in ("products", "carts", "orders", "discount_codes", "store_meta"):
        db[name].delete_many({})


def get_global_meta() -> dict:
    col = store_meta_collection()
    doc = col.find_one({"_id": "global"})
    if doc is None:
        doc = {"_id": "global", "completed_order_count": 0, "settings_overrides": {}}
        col.insert_one(doc)
    return doc
