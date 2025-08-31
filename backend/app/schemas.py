# app/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

# ---------- User ----------
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, max_length=255)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    created_at: Optional[datetime] = None

# ---------- Mutual Fund ----------
class MutualFundBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: Optional[str] = Field(default=None, max_length=100)
    nav: Optional[float] = None
    owner_id: Optional[int] = None

class MutualFundCreate(MutualFundBase):
    pass

class MutualFundUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    category: Optional[str] = Field(default=None, max_length=100)
    nav: Optional[float] = None
    owner_id: Optional[int] = None

class MutualFundOut(MutualFundBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
