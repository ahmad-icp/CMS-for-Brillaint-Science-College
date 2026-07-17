"""Shared pytest fixtures with isolated database and development auth overrides."""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import Header
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import app.db.models  # noqa: E402,F401
from app.core.security import CurrentUser, get_current_user  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    testing_session = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    with testing_session() as session:
        yield session
        session.rollback()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def app(db_session: Session):
    application = create_app()

    def override_get_db():
        yield db_session

    def override_current_user(
        x_user_id: str = Header(default="development-user"),
        x_college_id: str = Header(default="college-a"),
        x_role: str = Header(default="administrator"),
    ) -> CurrentUser:
        return CurrentUser(user_id=x_user_id, college_id=x_college_id, role=x_role)

    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_current_user] = override_current_user
    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
