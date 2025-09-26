"""Alembic configuration file for Sales Assistant."""
from __future__ import annotations

from logging.config import fileConfig
from typing import Generator

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.app.core.config import settings
from src.app.core.db import Base
from src.app.knowledge import models as knowledge_models  # noqa: F401 - ensure models registered

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url)

def get_target_metadata():  # pragma: no cover - metadata populated later
    return Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=get_target_metadata())

        with context.begin_transaction():
            context.run_migrations()


def main() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


main()
