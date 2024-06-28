import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import pool

# Add the src directory to the sys.path
sys.path.append(os.path.join(sys.path[0], "src"))

# Import your models and database configuration
from src import models
from src.config import db_host, db_name, db_pass, db_port, db_user, connection_string

# Set up logging configuration
config = context.config
fileConfig(config.config_file_name)

# Set database options from environment variables or imported config
section = config.config_ini_section
config.set_section_option(section, "DB_HOST", db_host)
config.set_section_option(section, "DB_PORT", db_port)
config.set_section_option(section, "DB_NAME", db_name)
config.set_section_option(section, "DB_PASS", db_pass)
config.set_section_option(section, "DB_USER", db_user)

# Set the connection string for Alembic
config.set_main_option("sqlalchemy.url", connection_string)
target_metadata = models.Base.metadata

# Create an asynchronous engine for the database connection
async_engine: AsyncEngine = create_async_engine(
    connection_string,
    poolclass=pool.NullPool,
    future=True,  # Use the future API for SQLAlchemy 2.0
)


# Define an asynchronous function to run migrations in online mode
async def run_migrations_online():
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


# Synchronous function to run migrations
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


# Define a function to run migrations in offline mode
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Execute migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
