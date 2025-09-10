# app/models.py

# -----------------------------
# SQLAlchemy models (existing)
# -----------------------------
from sqlalchemy import Column, Integer, String, DateTime, Numeric, func
from app.database import Base  # declarative base for legacy SQLAlchemy models

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


# -----------------------------
# Ormar model (v0.20+ style)
# -----------------------------
import ormar
from datetime import datetime, date,timezone
from app.database import base_ormar_config  # OrmarConfig with database & metadata

class FundNav(ormar.Model):
    ormar_config = base_ormar_config.copy(
        tablename="fund_navs",
        constraints=[ormar.UniqueColumns("fund_id", "date")],
    )

    id: int = ormar.Integer(primary_key=True)
    fund_id: str = ormar.String(max_length=255, index=True)
    date: date = ormar.Date(index=True)
    
    nav: float = ormar.Float()
    aum: float = ormar.Float(nullable=True)  # ✅ Correctly nullable
    scheme_name: str = ormar.String(max_length=500, nullable=True)  # ✅ Correctly nullable
    category: str = ormar.String(max_length=200, nullable=True)  # ✅ Correctly nullable
    
    source: str = ormar.String(max_length=100, default="api.mfapi.in")
    updated_at: datetime = ormar.DateTime(timezone=True, default=datetime.now(timezone.utc))


