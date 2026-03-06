# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (http://127.0.0.1:8000, Swagger UI at /docs)
fastapi dev ./app/main.py

# Run all tests
pytest -v

# Run a single test file
pytest app/tests/test_crud.py -v

# Run a single test by name
pytest -k "test_name" -v
```

## Architecture

FastAPI REST API for loan management and amortization schedule calculation. Uses SQLModel (SQLAlchemy + Pydantic) with an in-memory SQLite database.

### Key layers

- **`app/main.py`** — App entry point, creates FastAPI instance
- **`app/models.py`** — All SQLModel table and schema models (User, Loan, LoanShare, Token). Uses inheritance pattern: `XxxBase` → `Xxx(table=True)` → `XxxPublic`/`XxxCreate`
- **`app/crud.py`** — Database operations (create/update users, create loans, create loan shares)
- **`app/amortization_calculator.py`** — Amortization math using `Decimal` with `ROUND_HALF_UP` precision
- **`app/core/config.py`** — Pydantic Settings (secrets, token expiry, default superuser)
- **`app/core/db.py`** — SQLModel engine setup, DB init with default superuser (admin/ok)
- **`app/core/security.py`** — JWT token creation, password hashing (bcrypt via passlib)
- **`app/api/deps.py`** — FastAPI dependencies for auth (OAuth2 + JWT, current user extraction)
- **`app/api/routes/`** — Route handlers: `login.py`, `users.py`, `loans.py`

### API routes (all under `/api/v1`)

- `POST /login/access-token` — OAuth2 password flow
- `POST /users/` — Create user (superuser only)
- `POST /loans/` — Create loan
- `GET /loans/` — List user's owned + shared loans
- `GET /loans/{id}/schedule` — Full amortization schedule
- `GET /loans/{id}/summary?month=N` — Single month summary
- `PUT /loans/{id}/share?email=...` — Share loan read access (idempotent)

### Authorization model

Three levels: superuser (admin), authenticated owner, shared user. Loan access checks are in the route handlers — owners and shared users can view, only owners can share. The `LoanShare` table is a many-to-many junction between User and Loan.

## Testing

Tests live in `app/tests/`. Fixtures in `conftest.py` provide a session-scoped DB, module-scoped TestClient, and pre-built auth token headers for superuser and normal user. Test helpers in `app/tests/utils/` generate random test data.
