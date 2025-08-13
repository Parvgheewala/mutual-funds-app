from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    risk_profile = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MutualFund(Base):
    __tablename__ = "mutual_funds"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String)
    risk_level = Column(String)
    nav_history = Column(JSON)
    expense_ratio = Column(Float)

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action_type = Column(String)
    action_details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

