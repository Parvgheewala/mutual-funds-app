from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

# ---------- User ----------
class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

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
