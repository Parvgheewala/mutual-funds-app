# app/models.py
from app.database import Base, engine
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)


class MutualFund(Base):
    __tablename__ = "mutualfunds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    nav = Column(Numeric(10, 2), nullable=True)   # matches NUMERIC(10,2)
    created_at = Column(DateTime, server_default=func.now())  # DEFAULT CURRENT_TIMESTAMP


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
