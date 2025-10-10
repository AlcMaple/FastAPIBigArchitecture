# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI-based medical appointment system using a layered architecture pattern. Built with async/await, SQLModel ORM, and MySQL database.

## Common Commands

### Development
```bash
# Start development server
python main.py

# Run all tests
pytest

# Run specific test file
pytest testcase/test_sync_api.py

# Run tests with verbose output
pytest -v
```

### Database Setup
```bash
# Create production database
CREATE DATABASE arch_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create test database (if using MySQL for tests)
CREATE DATABASE arch_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Configure environment
cp .env.example .env
# Then edit .env with database credentials
```

### Access Points
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Static Files: http://localhost:8000/static/

## Architecture

### Layered Architecture (5 Layers)

Each feature module follows this structure:

```
apis/{module_name}/
├── api/           # API layer - HTTP request/response handling
├── services/      # Business logic layer - core domain logic
├── repository/    # Data access layer - database operations
├── schemas/       # Data model layer - Pydantic request/response models
└── dependencies/  # Dependency injection - shared dependencies
```

**Layer Flow**: API → Service → Repository → Database

**Key Principle**: Each layer only depends on the layer directly below it.

### Database Session Management

Two session types in [db/database.py](db/database.py):

1. **`depends_get_db_session()`** - For read operations (SELECT queries)
   - No automatic commit
   - Use in GET endpoints

2. **`depends_get_db_session_with_transaction()`** - For write operations (INSERT/UPDATE/DELETE)
   - Auto-commit on success
   - Auto-rollback on exception
   - Use in POST/PUT/DELETE endpoints
   - **Critical**: One request = one transaction. All database operations in a request must complete before commit.

Example:
```python
# Read operation
@router.get("/doctors")
async def get_doctors(db: AsyncSession = Depends(depends_get_db_session)):
    return await DoctorService.get_all_doctors(db)

# Write operation
@router.post("/doctor")
async def create_doctor(
    data: DoctorCreateRequest,
    db: AsyncSession = Depends(depends_get_db_session_with_transaction)
):
    return await DoctorService.create_doctor(db, data)
```

### Response Format

All API responses use standardized format from [exts/responses/json_response.py](exts/responses/json_response.py):

- **Success**: `Success(result={...}, message="...")` - Status 200, code 200
- **Fail**: `Fail(message="...")` - Status 200, code 1000+

Response structure:
```json
{
  "success": true,
  "code": 200,
  "message": "获取成功",
  "result": {...},
  "timestamp": 1234567890
}
```

### Exception Handling

Global exception handler in [exts/exceptions/handlers.py](exts/exceptions/handlers.py):

- **BusinessError**: Custom business logic errors (use `ExceptionEnum`)
- **ValueError**: Automatically caught and converted to `Fail` response
- **RequestValidationError**: Parameter validation errors
- **Other exceptions**: Logged and return appropriate error responses

Error code ranges:
- 200: Success
- 1000-1999: Parameter validation errors
- 2000-2999: User authentication/permission errors
- 3000-3999: Business logic errors
- 4000-4999: External service errors
- 5000-5999: Internal server errors

### Logging

Configured via [exts/logururoute/](exts/logururoute/):
- Business logger: `from exts.logururoute.business_logger import logger`
- Logs stored in [log/](log/) directory
- Logger middleware (commented out in [app.py](app.py)) can track all requests

## Database Models

Core entities in [db/models.py](db/models.py):

- **Doctor**: Medical staff information
- **Schedule**: Doctor scheduling (date, time slots, capacity)
- **Patient**: Patient records
- **Appointment**: Booking records linking doctors, patients, and schedules
- **Hospital**, **Department**, **MedicalRecord**: Supporting entities

Relationships:
- Doctor → Schedules (one-to-many)
- Doctor → Appointments (one-to-many)
- Patient → Appointments (one-to-many)
- Schedule → Appointments (one-to-many)

## Testing

Test configuration in [testcase/conftest.py](testcase/conftest.py):

- Tests use isolated database (SQLite in-memory by default, configurable to MySQL)
- Database recreated for each test session
- Test files must start with `test_` or end with `_test.py`
- Place test files in [testcase/](testcase/) directory

Test database configuration in `.env`:
- `TEST_DB_TYPE=sqlite` (default) or `mysql`
- `SQLITE_TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:`
- `TEST_DATABASE_URL=mysql+aiomysql://...` (for MySQL tests)

## File Upload Handling

File utilities in [utils/file.py](utils/file.py):

- `FileUtils.save_damage_image()`: Save uploaded files to [static/uploads/damage_images/](static/uploads/damage_images/)
- Files saved with UUID-based names to prevent conflicts
- Update database avatar field when uploading doctor avatars

## Configuration

Settings in [config/settings.py](config/settings.py):

- Uses Pydantic Settings for type-safe configuration
- Loads from `.env` file
- Database connection pool configuration (pool_size, max_overflow, pool_recycle, pool_timeout)
- Access via `from config.settings import settings`

## Key Design Patterns

1. **Dependency Injection**: Use FastAPI's `Depends()` for database sessions and other dependencies
2. **Async/Await**: All database operations and route handlers are async
3. **Repository Pattern**: Database operations isolated in repository layer
4. **Service Layer**: Business logic separated from API endpoints
5. **Schema Validation**: Pydantic models for request/response validation

## Adding New Features

To add a new module:

1. Create module directory under [apis/](apis/):
   ```
   apis/new_module/
   ├── api/          # Route definitions
   ├── services/     # Business logic
   ├── repository/   # Database operations
   ├── schemas/      # Pydantic models
   └── __init__.py
   ```

2. Define routers in `api/__init__.py`:
   ```python
   from fastapi import APIRouter
   router_new_module = APIRouter(prefix="/new_module", tags=["New Module"])
   ```

3. Register router in [apis/__init__.py](apis/__init__.py) and [app.py](app.py):
   ```python
   from apis import router_new_module
   app.include_router(router_new_module)
   ```

4. Add database models to [db/models.py](db/models.py) if needed
5. Follow the existing layer structure and naming conventions

## Project Structure Notes

- **[exts/](exts/)**: Global extensions (logging, responses, exceptions, request context)
- **[plugins/](plugins/)**: Custom plugins and third-party integrations
- **[middlewares/](middlewares/)**: Request/response middleware
- **[static/](static/)**: Static files (CSS, JS, uploaded files)
- **[wiki/](wiki/)**: Project documentation
- Root directory can contain custom modules (e.g., third-party SDK integrations)

## Important Conventions

- Use singular nouns for database table names (e.g., `doctor`, not `doctors`)
- All async functions should use `async`/`await` syntax
- Repository methods return dictionaries or lists of dictionaries (not ORM objects)
- Service layer validates business rules before calling repository
- API layer handles HTTP concerns only (validation, serialization)
