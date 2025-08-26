from fastapi import APIRouter, Depends
from .schemas import UserCreate, MutualFundCreate, UserOut, MutualFundOut
from .crud import create_user, create_mutualfund
from .database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

@router.post("/users/", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

@router.post("/mutualfunds/", response_model=MutualFundOut)
async def add_mutualfund(mf: MutualFundCreate, db: AsyncSession = Depends(get_db)):
    return await create_mutualfund(db, mf)
