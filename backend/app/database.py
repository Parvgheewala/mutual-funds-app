# app/database.py
import os
from typing import AsyncIterator, AsyncGenerator
from dotenv import load_dotenv
import databases
import sqlalchemy
import ormar
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base, sessionmaker  # Changed this line

# Load env
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ---------- SQLAlchemy (async) ----------
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Use sessionmaker instead of async_sessionmaker for compatibility
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()

# ---------- Ormar + databases ----------
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

base_ormar_config = ormar.OrmarConfig(
    database=database,
    metadata=metadata,
)

# ---------- Connection helpers ----------
async def connect_to_db():
    if not database.is_connected:
        await database.connect()

async def disconnect_from_db():
    if database.is_connected:
        await database.disconnect()

# ---------- Table creation ----------
async def create_tables_if_needed():
    """Create database tables using AsyncEngine with run_sync"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(metadata.create_all)
        
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

# ---------- Dependencies ----------
async def get_database() -> AsyncIterator[databases.Database]:
    yield database

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

get_db = get_async_session
