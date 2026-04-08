# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application (hot reload enabled)
python main.py
# App available at http://localhost:8000, docs at http://localhost:8000/docs

# Run all tests
pytest

# Run a single test file
pytest tests/integration/api/test_user.py -v

# Run tests matching a keyword
pytest -k "test_register" -v
```

## Environment Setup

Copy `.env.example` to `.env` and set the database URL:
```
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/arch_db
```

Create the MySQL database first:
```sql
CREATE DATABASE arch_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Tests use an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`) — no MySQL needed for testing.

## Architecture

### Application Bootstrap

- `main.py` — entry point (uvicorn runner)
- `app.py` — calls `AppFactory` to wire up all modules, mounts static files and sub-apps
- `app_factory.py` — `AppFactory` class that creates and composes FastAPI apps; holds the global rate limiter (`60/minute` default)

Each registered module gets its own sub-application with isolated docs at `/{module_name}/docs`.

### Module Structure

All business logic lives under `apis/`. Each module follows a strict four-layer pattern:

```
apis/<module_name>/
├── api/          # Route handlers — call services, return Success/Error
├── services/     # Business logic — validate, orchestrate, call repositories
├── repository/   # Database queries via SQLAlchemy async sessions
├── schemas/      # Pydantic/SQLModel request & response models
```

Currently one module exists: `apis/base/` (registered as `"simple"`).

To add a new module: create the directory tree above, register it in `app.py` with `factory.register_module(...)`.

### Key Extension Points (`exts/`)

- **`exts/responses/api_response.py`** — `Success(data, message)` and `Error(code, message)` are the only response types used in route handlers. All responses share the envelope `{success, code, message, data, timestamp}`.
- **`exts/exceptions/api_exception.py`** — raise `ApiException(ErrorCode.XXX)` for all error conditions; the global handler converts it to an `Error` response automatically.
- **`exts/exceptions/error_code.py`** — `ErrorCode` enum defining all error codes (ranges: 1000–1999 param errors, 2000–2999 auth/authz, 3000–3999 business, 4000–4999 resource/external, 5000–5999 system).
- **`exts/auth.py`** — `get_current_user_id` dependency; inject with `Depends(get_current_user_id)` in route handlers to require authentication.

### Database (`db/`)

- `db/database.py` — two async session dependencies for injection:
  - `depends_get_db_session` — plain session, manual commit needed
  - `depends_get_db_session_with_transaction` — auto-commit on success, auto-rollback on exception
- `db/models.py` — SQLModel table definitions
- `db/init_db.py` — `init_database()` to create all tables (currently commented out in lifespan; run manually or uncomment)

### Configuration (`config/settings.py`)

Pydantic `Settings` class reads from `.env`. Key settings: `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `TEST_DATABASE_URL`.

### Rate Limiting

The `AppFactory` owns a single `slowapi` `Limiter`. Route handlers that need custom limits import it via `get_app_factory().limiter` and apply `@limiter.limit("N/minute")` alongside the `Request` parameter.

### Utils (`utils/`)

- `utils/jwt.py` — JWT encode/decode
- `utils/password.py` — argon2 password hashing (async-safe)
- `utils/file.py` — async file I/O helpers
- `utils/datetime.py` — date/time utilities
- `utils/type.py` — type conversion helpers

## Testing Conventions

Integration tests use `httpx.AsyncClient` with `ASGITransport` pointed at the main `app`. The `client` fixture in `tests/integration/conftest.py` overrides both DB session dependencies with a fresh in-memory SQLite session per test.

Unit tests live under `tests/unit/`; integration tests under `tests/integration/api/`.

Test factories are in `tests/factories.py` (built with `polyfactory` and `faker`).
