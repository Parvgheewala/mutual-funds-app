# app/models.py
from app.database import Base, engine
from sqlalchemy import Column, Integer, String, DateTime, func, Numeric

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class MutualFund(Base):
    __tablename__ = "mutualfunds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    nav = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
