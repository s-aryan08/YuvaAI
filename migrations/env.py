"""
YuvaAI - Alembic Migration Configuration

Connects Alembic to the existing PostgreSQL database
and registers SQLAlchemy models for migrations.
"""

from logging.config import fileConfig

from alembic import context

from backend.database import Base, engine
from backend.config import DATABASE_URL

# Import models so SQLAlchemy registers all tables.
import backend.models


# ==========================================
# 1. ALEMBIC CONFIGURATION
# ==========================================

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ==========================================
# 2. SQLALCHEMY METADATA
# ==========================================

target_metadata = Base.metadata


# ==========================================
# 3. OFFLINE MIGRATIONS
# ==========================================

def run_migrations_offline():

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


# ==========================================
# 4. ONLINE MIGRATIONS
# ==========================================

def run_migrations_online():

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


# ==========================================
# 5. EXECUTE MIGRATIONS
# ==========================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()