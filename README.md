# Ecommerce Cart API

A Django REST Framework backend for an ecommerce store with cart management, checkout, and an nth-order discount reward system.

## Features

- Add items to a customer cart and view cart totals
- Checkout with optional discount code validation
- Automatic discount code generation every *n* completed orders
- Admin API to manually generate discount codes and view store stats
- MongoDB persistence for products, carts, orders, discounts, and settings

## Prerequisites

- Python 3.11+
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) cluster (free tier works)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### MongoDB Atlas

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com).
2. **Database Access** — create a database user with read/write permissions.
3. **Network Access** — add your IP (or `0.0.0.0/0` for development).
4. **Database → Connect → Drivers** — copy the Python connection string.
5. Paste it into `.env` as `MONGODB_URI` (replace `<password>` with your user password):

```env
MONGODB_URI=mongodb+srv://myuser:mypassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DB_NAME=cart_store
```

> Tests use a separate database (`cart_store_test`) on the same Atlas cluster.

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | *(required)* | MongoDB Atlas SRV connection string (`mongodb+srv://...`) |
| `MONGODB_DB_NAME` | `cart_store` | Database name for application data |
| `DISCOUNT_EVERY_N_ORDERS` | `3` | Issue a discount code every nth completed order |
| `DISCOUNT_PERCENT` | `10` | Discount percentage for generated codes |
| `DISCOUNT_CODE_PREFIX` | `SAVE` | Prefix for generated codes (e.g. `SAVE-3-A1B2C3`) |
| `ADMIN_API_KEY` | `dev-admin-key` | Required `X-Admin-Key` header for admin endpoints |

## Run

```bash
python manage.py check_mongodb   # verify Atlas connection
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | Customer shop UI |
| `http://localhost:8000/admin/` | Admin dashboard UI |
| `http://localhost:8000/api/` | REST API |

DRF browsable API is available on GET endpoints in the browser.

## API Endpoints

### Customer

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List product catalog |
| POST | `/api/carts/{customer_id}/items/` | Add item to cart |
| GET | `/api/carts/{customer_id}/` | View cart with totals |
| POST | `/api/checkout/` | Place order |
| GET | `/api/customers/{customer_id}/profile/` | Order count, spend, and purchase history |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/discount-codes/generate/` | Manually generate a discount code anytime |
| GET | `/api/admin/stats/` | Store statistics |
| GET | `/api/admin/customers/` | All customers with order summaries |
| GET | `/api/admin/customers/{customer_id}/` | Full purchase history for a customer |
| GET / PATCH | `/api/admin/settings/` | View or update discount rules |

Admin endpoints require header: `X-Admin-Key: dev-admin-key`

## Example Flow

```bash
# List products
curl http://localhost:8000/api/products/

# Add items to cart
curl -X POST http://localhost:8000/api/carts/alice/items/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod-1", "quantity": 2}'

# View cart
curl http://localhost:8000/api/carts/alice/

# Checkout
curl -X POST http://localhost:8000/api/checkout/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "alice"}'

# Checkout with discount code
curl -X POST http://localhost:8000/api/checkout/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "alice", "discount_code": "SAVE-3-A1B2C3"}'

# Admin stats
curl http://localhost:8000/api/admin/stats/ \
  -H "X-Admin-Key: dev-admin-key"
```

## Tests

```bash
python manage.py test store
```

## Postman

Import [`postman/ecommerce-cart.postman_collection.json`](postman/ecommerce-cart.postman_collection.json) for ready-made requests.

## Web UI

**Customer (`/`):** Browse products, add to cart, checkout with optional discount code. Enter your name to identify your cart (saved in browser).

**Admin (`/admin/`):** View store stats, configure discount rules (every N orders, percent, code prefix), browse all customers and their purchase history, and manually generate discount codes. Enter the admin API key (`dev-admin-key` by default) — stored in browser session only.

**Customer purchase count:** The shop page shows how many orders you've placed and your total spend. A purchase history section lists past orders with line items.

## Project Structure

```
config/          # Django settings and root URLs
store/
  domain.py      # Domain dataclasses
  repositories/  # MongoDB data access (pymongo)
  services/      # Business logic
  views/         # DRF API views + template UI views
  templates/     # Customer and admin HTML pages
  static/        # CSS and JavaScript
  tests/         # Unit and integration tests
```

## Design Decisions

See [DECISIONS.md](DECISIONS.md) for detailed rationale behind key architectural choices.
