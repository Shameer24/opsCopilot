from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your SQLAlchemy Base metadata for autogenerate.
# IMPORTANT: keep a single authoritative Base import.
# If this import fails, fix the path to where your declarative Base lives.
from app.db.base import Base  # noqa: E402, F401

# Ensure pgvector types are importable during autogenerate/migrations.
# (Migration scripts may reference pgvector.sqlalchemy.vector.VECTOR)
import pgvector.sqlalchemy  # noqa: F401

# Ensure all model modules are imported so Base.metadata is populated for autogenerate.
# If you don't import model modules, Alembic sees an empty Base.metadata and generates empty migrations.
import importlib
import pkgutil

def _import_submodules(pkg_name: str) -> None:
    """Import a package and all its submodules (best-effort)."""
    try:
        pkg = importlib.import_module(pkg_name)
    except Exception:
        return

    # If it's a package, walk its submodules
    pkg_path = getattr(pkg, "__path__", None)
    if not pkg_path:
        return

    for m in pkgutil.walk_packages(pkg_path, prefix=pkg.__name__ + "."):
        try:
            importlib.import_module(m.name)
        except Exception:
            # Ignore individual import failures; autogenerate only needs the modules that load.
            pass

# Common locations for SQLAlchemy models in this repo.
# Adjust/add package names if your models live elsewhere.
_import_submodules("app.db.models")
_import_submodules("app.models")

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    import os

    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    import os
    from sqlalchemy import create_engine

    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
