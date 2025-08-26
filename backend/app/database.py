# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.automap import automap_base
from dotenv import load_dotenv
import os

# Load .env from backend folder
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Declarative base
Base = declarative_base()

# Optional: automap base if you need reflection elsewhere
AutomapBase = automap_base()

# FastAPI dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
