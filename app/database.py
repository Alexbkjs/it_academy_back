from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the database URL from environment variables
database_url = os.getenv("DATABASE_URL")

# Create an asynchronous SQLAlchemy engine connected to the database
# 'echo=True' enables SQL statement logging for debugging
engine = create_async_engine(database_url, echo=True)

# Create an asynchronous session factory for managing database sessions
AsyncSessionLocal = sessionmaker(
    bind=engine,  # Bind the session to the asynchronous engine
    class_=AsyncSession,  # Use AsyncSession for asynchronous operations
    expire_on_commit=False,  # Prevent automatic expiration of instances after commit
)

# Create a base class for declarative models
Base = declarative_base()

# Dependency to get a database session
# Uses asynchronous context manager to ensure proper session handling
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session  # Provide the session to the caller, ensuring it's properly closed
