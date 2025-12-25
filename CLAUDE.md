# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI-based web framework using a layered architecture pattern. This is a Chinese-language medical appointment system (doctor/hospital/patient) that serves as a template for building FastAPI applications with clean architecture.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server (with auto-reload)
python main.py
# App runs at http://localhost:8000
# API docs at http://localhost:8000/docs

# Run all tests
pytest

# Run specific test file
pytest tests/integration/api/test_design_unit.py

# Run specific test function
pytest tests/integration/api/test_design_unit.py::test_create_design_unit_success

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_create"
```

## Architecture

### Five-Layer Pattern

Every functional module follows this structure:

```
apis/{module_name}/
├── api/          # API layer - routes, request/response handling
├── services/     # Business logic layer - core business rules
├── repository/   # Data access layer - database operations
├── schemas/      # Data models - Pydantic request/response models
└── dependencies/ # Dependency injection (optional)
```

**Data Flow**: `API → Service → Repository → Database`

### Key Directories

- **apis/**: Feature modules (each with full 5-layer structure)
- **db/**: Database configuration, models (SQLModel), initialization
- **exts/**: Global extensions (exceptions, responses, logging, request context)
- **middlewares/**: Request/response middleware (logger middleware)
- **plugins/**: Custom plugins and third-party integrations
- **config/**: Pydantic-based settings with `.env` support
- **tests/**: Integration and unit tests
- **utils/**: Utility functions and helper scripts

### Application Factory Pattern

The app uses a factory pattern ([app_factory.py](app_factory.py)) that:
1. Registers modules with `app_factory.register_module(name, router, description)`
2. Creates main app and module sub-apps via `create_all_apps(lifespan)`
3. Mounts sub-apps at `/{module_name}` for modular API documentation

Each module gets its own Swagger docs at `http://localhost:8000/{module_name}/docs`

## Database

### Configuration

- ORM: SQLModel (built on SQLAlchemy 2.0)
- Async driver: aiomysql for MySQL, aiosqlite for tests
- Connection pooling configured in [config/settings.py](config/settings.py)
- Two dependency injection functions:
  - `depends_get_db_session`: Basic session
  - `depends_get_db_session_with_transaction`: Auto-commit/rollback on success/error

### Database Models

Defined in [db/models.py](db/models.py) using SQLModel (combines Pydantic + SQLAlchemy).

## Response Format

All API responses use standardized format from [exts/responses/api_response.py](exts/responses/api_response.py):

```python
# Success response
return Success(data=result, message="操作成功")

# Returns:
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {...},
  "timestamp": 1678886400000
}
```

**Custom JSON encoder** handles datetime, Decimal, Pydantic models, SQLAlchemy models automatically.

## Exception Handling

Use `ApiException` from [exts/exceptions/api_exception.py](exts/exceptions/api_exception.py):

```python
from exts.exceptions.api_exception import ApiException
from exts.exceptions.error_code import ErrorCode

# Raise with default message
raise ApiException(ErrorCode.NOT_FOUND)

# Custom message
raise ApiException(ErrorCode.NOT_FOUND, "医生不存在")

# With additional data
raise ApiException(ErrorCode.VALIDATION_ERROR, "数据验证失败", data={"field": "phone"})
```

Global exception handler (`GlobalExceptionHandler`) automatically converts exceptions to proper API responses.

## Testing

### Test Structure

```
tests/
├── conftest.py              # Global fixtures (event loop)
├── factories.py             # Polyfactory model factories
├── integration/
│   ├── conftest.py         # Integration test fixtures (db_session, client)
│   ├── api/                # API endpoint tests
│   └── repositories/       # Repository layer tests
└── unit/
    ├── conftest.py         # Unit test fixtures
    ├── services/           # Service layer tests
    └── utils/              # Utility tests
```

### Test Database

- Uses SQLite in-memory database (`sqlite+aiosqlite:///:memory:`)
- No configuration needed - works out of the box
- Each test function gets fresh database (auto create/drop tables)
- Fast, isolated, and automatically cleaned up

### Test Fixtures (Integration)

- `db_session`: Async database session with auto create/drop tables
- `client`: AsyncClient with dependency overrides for testing
- `clean_db`: Clears database data while preserving schema

### Test Factories

Uses Polyfactory with custom async persistence ([tests/factories.py](tests/factories.py)):

```python
# Create test data
user = await UserFactory.create_async(session=db_session, name="张三")
```

### Test Utilities

[tests/integration/api/utils.py](tests/integration/api/utils.py) provides:
- `assert_api_success(response)`: Validates success response, returns data
- `assert_api_failure(response, expected_code, match_msg, status_code)`: Validates error response

### Parametrized Tests

Use `@pytest.mark.parametrize` for testing multiple scenarios:

```python
@pytest.mark.parametrize(
    "field, bad_value, expected_msg",
    [
        ("email", "not-an-email", "邮箱格式"),
        ("tel", "123", "手机号格式"),
    ],
)
@pytest.mark.asyncio
async def test_validation(client, field, bad_value, expected_msg):
    ...
```

## Adding New Modules

1. Create module directory: `apis/{module_name}/`
2. Add subdirectories: `api/`, `services/`, `repository/`, `schemas/`
3. Define routes in `api/` with APIRouter
4. Register in [apis/__init__.py](apis/__init__.py):
   ```python
   from .{module_name}.api import router_{module_name}
   router_{module_name}_module = APIRouter()
   router_{module_name}_module.include_router(router_{module_name})
   ```
5. Register in [app.py](app.py):
   ```python
   factory.register_module("{module_name}", router_{module_name}_module, "模块描述")
   ```

## Code Style

- **Type hints required**: All function signatures use Python type annotations
- **Async/await**: All I/O operations are async
- **Dependency injection**: Use FastAPI's `Depends()` for database sessions
- **Chinese comments/messages**: Business logic comments and user-facing messages in Chinese
- **Table naming**: Singular nouns (e.g., `user`, not `users`)

## Configuration

Environment variables loaded from `.env` file (see `.env.example`):
- `DATABASE_URL`: MySQL connection string
- `TEST_DATABASE_URL`: SQLite in-memory database (default: `sqlite+aiosqlite:///:memory:`)
- Application settings in [config/settings.py](config/settings.py) using Pydantic Settings

## Logging

Uses Loguru ([exts/logururoute/](exts/logururoute/)):
- Structured logging with business logger
- Optional request/response logging middleware (commented in [app.py](app.py))
- Logs stored in `logs/` directory

## Important Patterns

1. **Session Management**: Always use dependency injection for database sessions
2. **Transaction Handling**: Use `depends_get_db_session_with_transaction` for write operations
3. **Error Responses**: Raise `ApiException` rather than returning error responses
4. **Schema Validation**: Use Pydantic models for request/response validation
5. **Factory Pattern**: Test data creation via Polyfactory factories, not manual model instantiation
