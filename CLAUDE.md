# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the application:**
```bash
uvicorn app:app --reload
```

**Initialize database tables manually:**
```bash
python -m db.init_db
```

**Database Setup:**
1. Create MySQL database: `arch_db`
2. Copy `.env.example` to `.env` and update database credentials
3. Tables will be auto-created on application startup

## Architecture Overview

This is a FastAPI-based medical management system with a layered architecture:

### Core Structure
- **Entry Point**: `app.py` - Main FastAPI application with middleware, CORS, router registration, and database initialization
- **Routing**: Organized by feature modules in `apis/` directory
- **Database**: SQLModel + SQLAlchemy with async MySQL support (aiomysql driver)
- **Models**: All database tables defined in `db/models.py` with proper relationships
- **Response Format**: Standardized Success/Fail responses via `exts.responses`

### Module Organization Pattern
Each feature module (e.g., `apis/doctor/`) follows a consistent 4-layer pattern:
- `api/` - FastAPI route handlers and HTTP logic
- `services/` - Business logic layer
- `repository/` - Data access layer
- `schemas/` - Pydantic models for request/response

### Key Components
- **Database Models**: Complete medical system models in `db/models.py` (Doctor, Patient, Appointment, Schedule, etc.)
- **Database Connection**: Async MySQL connection and session management in `db/database.py`
- **Database Initialization**: Auto table creation via `db/init_db.py`
- **Middleware**: Custom logging middleware in `middlewares/`
- **Extensions**: Reusable components in `exts/` (exceptions, responses, etc.)
- **Configuration**: Centralized settings in `config/settings.py`

### Router Registration
- Routers are imported in `apis/__init__.py` and registered in `app.py`
- Each module exports its router with appropriate prefix and tags
- Doctor module uses prefix `/api/v1` with tag "医生信息模块"

### Database Session Management
- Uses dependency injection pattern: `db_session: AsyncSession = Depends(depends_get_db_session)`
- All database operations are async

### Error Handling
- Services raise `ValueError` for business logic errors
- Controllers catch exceptions and return standardized `Success`/`Fail` responses
- HTTP status codes are embedded in response objects

## Key Files to Understand
- `app.py` - Application setup and configuration
- `apis/doctor/api/doctor.py` - Example of API layer implementation
- `apis/doctor/__init__.py` - Module exports pattern
- `exts/responses/` - Response formatting utilities