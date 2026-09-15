import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

from dotenv import load_dotenv

# Add src/backend to path so models can be imported.
_here = Path(__file__).resolve().parent
load_dotenv(_here.parent / ".env")
load_dotenv(_here.parent / "src" / "backend" / ".env")

for candidate in (_here.parent / "src" / "backend", _here.parent / "backend"):
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        break

from database.models import Base  # noqa: E402


config = context.config

# Allow callers (including isolated test runs / Docker) to override the URL.
# TEST_DATABASE_URL_SYNC takes precedence over DATABASE_URL_SYNC.
raw_async_url = os.environ.get("DATABASE_URL", "")
fallback_sync_url = (
    raw_async_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    .replace("?ssl=require", "?sslmode=require")
    if raw_async_url else None
)

db_url = (
    os.environ.get("TEST_DATABASE_URL_SYNC")
    or os.environ.get("ALEMBIC_DATABASE_URL")
    or os.environ.get("DATABASE_URL_SYNC")
    or fallback_sync_url
)
from sqlalchemy import create_engine

if db_url:
    # Escape percent signs for configparser safely
    config.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = db_url or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    if db_url:
        connectable = create_engine(db_url, poolclass=pool.NullPool)
    else:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()



if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
