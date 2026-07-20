from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, make_url, pool, text

import app.db.models  # noqa: F401
from app.core.config import settings
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = make_url(settings.DATABASE_URL)
    connect_args = {"connect_timeout": settings.DB_CONNECT_TIMEOUT_SECONDS} if url.get_backend_name() == "postgresql" else {}
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    with connectable.connect() as connection:
        if connection.dialect.name == "postgresql":
            lock_ms = int(settings.MIGRATION_LOCK_TIMEOUT_SECONDS * 1000)
            statement_ms = int(settings.DB_STATEMENT_TIMEOUT_SECONDS * 1000)
            connection.execute(
                text("SELECT set_config('lock_timeout', :timeout, false)"),
                {"timeout": f"{lock_ms}ms"},
            )
            connection.execute(
                text("SELECT set_config('statement_timeout', :timeout, false)"),
                {"timeout": f"{statement_ms}ms"},
            )
            locked = connection.execute(text("SELECT pg_try_advisory_lock(2026072001)")).scalar()
            if not locked:
                raise RuntimeError("Another database migration is already running; refusing to wait forever.")
        try:
            context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
            with context.begin_transaction():
                context.run_migrations()
        finally:
            if connection.dialect.name == "postgresql":
                connection.execute(text("SELECT pg_advisory_unlock(2026072001)"))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
