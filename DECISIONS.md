# Design Decisions

## Decision: Django + DRF for the API layer

**Context:** The assignment requires a backend API with validation, error handling, and tests. The team primarily uses TypeScript/Node.js, but Python was chosen for this implementation.

**Options Considered:**
- Option A: FastAPI — lightweight, async-native, Pydantic validation
- Option B: Django + Django REST Framework — batteries-included project structure, serializers, permissions, test client

**Choice:** Django + DRF

**Why:** Django provides a well-understood project layout (`settings`, `urls`, apps) that scales cleanly. DRF serializers handle request validation and response shaping without boilerplate. The browsable API aids manual testing without a frontend. FastAPI would be faster to scaffold for a pure API, but Django's conventions better demonstrate structured backend design for a take-home exercise.

---

## Decision: In-memory repositories instead of Django ORM

**Context:** The assignment explicitly allows in-memory storage with no database required.

**Options Considered:**
- Option A: Django models with SQLite — idiomatic Django, supports migrations
- Option B: In-memory Python dicts behind a repository layer — no persistence, no migrations

**Choice:** In-memory repositories with thread-safe locking

**Why:** This directly satisfies the "no database needed" constraint while keeping business logic in a dedicated service layer that is easy to unit test. A `MemoryStore` singleton with `threading.Lock` prevents race conditions on concurrent requests. The repository interface could later be swapped for ORM-backed implementations without changing services or views.

---

## Decision: Service layer separate from DRF views

**Context:** Core business logic (cart merging, discount validation, nth-order rules) must be unit tested independently of HTTP.

**Options Considered:**
- Option A: Business logic in DRF views/serializers — fewer files, faster to write
- Option B: Dedicated service classes called by thin views — more layers, better testability

**Choice:** Service layer (`CartService`, `CheckoutService`, `DiscountService`, `StatsService`)

**Why:** Views only handle HTTP concerns (parsing, status codes). Services encapsulate rules like "merge duplicate cart items" and "reject used discount codes." Unit tests run against services directly without spinning up the HTTP stack, making failures faster to diagnose and tests more focused.

---

## Decision: Customer identity via simple `customer_id` string

**Context:** The assignment does not require user authentication or account management.

**Options Considered:**
- Option A: Django auth with user accounts and sessions
- Option B: Opaque `customer_id` string in URL/body — caller provides identity

**Choice:** `customer_id` string (e.g. `alice`, `user-123`)

**Why:** Authentication is out of scope and would add significant complexity (registration, tokens, permissions). A string key is sufficient to demonstrate cart isolation per customer. In production, this would be replaced by an authenticated user ID from a JWT or session.

---

## Decision: Auto-generate discount on checkout + admin manual override

**Context:** Every nth completed order should produce a discount code. The assignment also requires an admin API to generate codes when the condition is satisfied.

**Options Considered:**
- Option A: Only auto-generate at checkout — no admin generate endpoint needed
- Option B: Only admin manually generates — no automatic reward
- Option C: Auto-generate at checkout AND admin endpoint for manual retry/override

**Choice:** Option C — both auto and manual

**Why:** Auto-generation gives customers a seamless reward experience immediately after the milestone order. The admin endpoint handles edge cases (e.g. generation failed, ops wants to re-issue) and satisfies the explicit admin API requirement. Generation is idempotent: if an unused code already exists for the current milestone, the same code is returned rather than creating duplicates.

---

## Decision: Environment-based configuration for n and x

**Context:** The discount rule "every nth order gets x% off" needs configurable values.

**Options Considered:**
- Option A: Hardcoded constants in code
- Option B: Environment variables with sensible defaults
- Option C: Admin API to change n and x at runtime

**Choice:** Environment variables via `django-environ`

**Why:** Env vars allow different values per deployment (staging vs production) without code changes. Hardcoding is too rigid; a runtime admin config API is over-engineering for this scope. Defaults (`n=3`, `x=10`) are documented in `.env.example`.

---

## Decision: Post-discount total as revenue in admin stats

**Context:** Admin stats must report revenue and total discounts given.

**Options Considered:**
- Option A: Revenue = sum of pre-discount subtotals (gross)
- Option B: Revenue = sum of post-discount order totals (net)

**Choice:** Revenue is the sum of `order.total` (after discounts)

**Why:** "Revenue" in ecommerce typically reflects what customers actually paid. `total_discounts_given` is tracked separately as the sum of `order.discount_amount`, so both gross and net figures can be derived. This avoids double-counting discounts in the revenue figure.

---

## Decision: Admin API key header instead of full auth

**Context:** Admin endpoints (stats, discount generation) should not be publicly accessible but full auth is out of scope.

**Options Considered:**
- Option A: No protection — open admin endpoints
- Option B: Simple shared secret via `X-Admin-Key` header
- Option C: Django admin + staff user sessions

**Choice:** `X-Admin-Key` header checked by a DRF `AdminAPIKeyPermission` class

**Why:** Provides a minimal access gate that is easy to test and document without building a user management system. The key is configurable via `ADMIN_API_KEY` env var. Production would use proper role-based auth (OAuth, API gateway, etc.).
