import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


db_host = os.getenv("MY_POSTGRES_RDS_ENDPOINT", "db:5432")

# Construct the full DATABASE_URL
DATABASE_URL = f"postgresql+asyncpg://admintest:password123!@{db_host}/mydb"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
