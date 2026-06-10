# Ecommerce Cart API

A Django REST Framework backend for an ecommerce store with cart management, checkout, and an nth-order discount reward system.

## Features

- Add items to a customer cart and view cart totals
- Checkout with optional discount code validation
- Automatic discount code generation every *n* completed orders
- Admin API to manually generate discount codes and view store stats
- In-memory storage (no database required for business data)

## Prerequisites

- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCOUNT_EVERY_N_ORDERS` | `3` | Issue a discount code every nth completed order |
| `DISCOUNT_PERCENT` | `10` | Discount percentage for generated codes |
| `DISCOUNT_CODE_PREFIX` | `SAVE` | Prefix for generated codes (e.g. `SAVE-3-A1B2C3`) |
| `ADMIN_API_KEY` | `dev-admin-key` | Required `X-Admin-Key` header for admin endpoints |

## Run

```bash
python manage.py runserver
```

API base URL: `http://localhost:8000/api/`

DRF browsable API is available on GET endpoints in the browser.

## API Endpoints

### Customer

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List product catalog |
| POST | `/api/carts/{customer_id}/items/` | Add item to cart |
| GET | `/api/carts/{customer_id}/` | View cart with totals |
| POST | `/api/checkout/` | Place order |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/discount-codes/generate/` | Manually generate discount code (if milestone reached) |
| GET | `/api/admin/stats/` | Store statistics |

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

## Project Structure

```
config/          # Django settings and root URLs
store/
  domain.py      # Domain dataclasses
  repositories/  # In-memory data access
  services/      # Business logic
  views/         # Thin DRF API views
  tests/         # Unit and integration tests
```

## Design Decisions

See [DECISIONS.md](DECISIONS.md) for detailed rationale behind key architectural choices.
