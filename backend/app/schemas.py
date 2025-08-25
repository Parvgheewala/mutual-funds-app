from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    risk_profile: Optional[str]

class UserOut(BaseModel):
    id: str
    email: EmailStr
    risk_profile: Optional[str]

class MutualFundCreate(BaseModel):
    name: str
    category: Optional[str]
    risk_level: Optional[str]
    nav_history: Optional[Dict]
    expense_ratio: Optional[float]

class MutualFundOut(BaseModel):
    id: str
    name: str
    category: Optional[str]
    risk_level: Optional[str]
    nav_history: Optional[Dict]
    expense_ratio: Optional[float]
