import os
import asyncio
import asyncpg

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def wait_for_db():
    while True:
        try:
            # Retrieve database connection parameters from environment variables
            dbname = os.getenv("POSTGRES_DB")
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            host = os.getenv("POSTGRES_HOST")
            # host = "db"  # Service name in Docker Compose
            port = "5432"
            # Attempt to connect to the database
            conn = await asyncpg.connect(
                user=user, password=password, database=dbname, host=host, port=port
            )
            print("success")
            await conn.close()
            break
        except Exception:
            print("Waiting for PostgreSQL to be ready...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(wait_for_db())
