from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URLs based on environment variables or any other source
url_db1 = os.environ.get("DEV_DATABASE_URL")
url_db2 = os.environ.get("TEST_DATABASE_URL")

# Modify the database URLs in the Alembic config
config.set_section_option("devdb", "sqlalchemy.url", url_db1)
config.set_section_option("testdb", "sqlalchemy.url", url_db2)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,user_module_prefix="pgvector.sqlalchemy.")

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
