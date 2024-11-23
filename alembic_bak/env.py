from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context
import asyncio
import os
from dotenv import load_dotenv

# Import your Base and models here
from app.models import (
    User,
    Quest,
    Achievement,
    UserQuestProgress,
    Requirement,
    Reward,
)  # Import all your models
from app.database import Base

# Load environment variables
load_dotenv()

# Get the target metadata from Base
target_metadata = Base.metadata

# Alembic Config object
config = context.config

# Set up logging
fileConfig(config.config_file_name)

# Load the DATABASE_URL from the .env file
# DATABASE_URL = "postgresql+asyncpg://admin:pass@fastapi-postgres/iar_db"
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    async with engine.connect() as connection:
        # Use `run_sync` to handle sync operations
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """Run migrations with a synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
