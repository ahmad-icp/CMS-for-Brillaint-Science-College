"""
Pytest configuration for the CMS application.

This module ensures:
- Models are imported exactly ONCE at session scope (before any tests run)
- A shared in-memory SQLite database is used across all tests
- Each test gets a clean schema (dropped and recreated)
- All fixtures use the same Base instance to avoid table redefinition errors
"""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# ✅ CRITICAL: Import models EXACTLY ONCE at module level, before any tests run.
# This ensures all ORM models register their tables with Base.metadata exactly once.
from app.db.base import Base  # noqa: E402
from app.core.security import CurrentUser, get_current_user  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402
import app.db.models  # noqa: E402,F401


@pytest.fixture(scope="session", autouse=True)
def _ensure_models_loaded_once():
    """
    Session-scoped auto-use fixture to guarantee models are loaded exactly once.
    
    This runs before ANY test or other fixture, ensuring:
    - app.db.models is imported (side effect: all tables register with Base)
    - No test can trigger a second import
    
    By using 'autouse=True', we guarantee this runs first, even if no test
    explicitly depends on it.
    """
    # Models already imported at module level, but this fixture ensures
    # the import happens during session setup, not during collection.
    pass


@pytest.fixture(scope="session")
def test_engine():
    """
    Create ONE in-memory SQLite engine for the entire test session.

    Uses StaticPool to keep the in-memory database alive across multiple
    connection acquisitions. This is safe because each test gets a fresh
    schema via drop_all/create_all in the db_session fixture.

    Benefits:
    - Single engine instance = consistent Base.metadata
    - No table redefinition errors
    - Minimal database setup overhead
    """
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Optional: Enable SQLite foreign keys for referential integrity testing
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Provide a fresh schema and SQLAlchemy session for each test.

    This fixture:
    1. Drops all tables from the shared engine
    2. Recreates all tables (using the ONE Base.metadata instance)
    3. Creates a new sessionmaker bound to the shared engine
    4. Yields a session for the test
    5. Cleans up by rolling back and dropping tables

    Why this prevents SQLAlchemy errors:
    - Uses the shared Base.metadata (defined in app/db/base.py)
    - Tables only exist during the test (drop_all before, drop_all after)
    - No multiple imports of models
    - No duplicate table definitions across tests
    - All tests use the same engine and Base instance

    **IMPORTANT**: Every unit test should use this fixture, not create its own engine.
    """
    # Clean slate: remove any tables from a previous test
    Base.metadata.drop_all(bind=test_engine)
    
    # Recreate all tables. This is safe because:
    # - app.db.models was imported at session scope (models_loaded fixture)
    # - Base.metadata contains all ORM model tables, registered exactly once
    # - No duplicate table definitions here
    Base.metadata.create_all(bind=test_engine)
    
    # Create a fresh sessionmaker for this test
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    
    # Yield the session to the test
    with TestingSessionLocal() as session:
        yield session
        # Best-effort cleanup: rollback any pending transactions
        session.rollback()
    
    # Post-test cleanup: remove all tables to avoid cross-test contamination
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def app(db_session: Session):
    """
    Create a FastAPI application instance wired to the per-test database session.

    Overrides the normal database dependency with the test session,
    so all API requests in integration tests use the in-memory test DB.
    """
    application = create_app()

    def override_get_db():
        yield db_session

    application.dependency_overrides[get_db] = override_get_db

    def override_get_current_user():
        return CurrentUser(user_id="test-admin", college_id="college-demo", role="administrator")

    application.dependency_overrides[get_current_user] = override_get_current_user
    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture()
def client(app):
    """
    Create a FastAPI TestClient for making HTTP requests in integration tests.
    """
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
