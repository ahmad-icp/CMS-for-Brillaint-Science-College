import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402
import app.db.models  # noqa: E402,F401


@pytest.fixture(scope="session")
def test_engine():
    """Create one in-memory SQLite engine for the test session.

    StaticPool keeps the in-memory database alive across connections while each
    test still gets an isolated schema rebuild in ``db_session``.
    """
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """Provide a fresh schema and SQLAlchemy session for each test."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    with TestingSessionLocal() as session:
        yield session
        session.rollback()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def app(db_session: Session):
    """Create a FastAPI app wired to the per-test database session."""
    application = create_app()

    def override_get_db():
        yield db_session

    application.dependency_overrides[get_db] = override_get_db
    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
