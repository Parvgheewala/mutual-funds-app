# app/userdata.py
from fastapi import APIRouter, Depends
from .schemas import UserCreate, MutualFundCreate, UserOut, MutualFundOut
from .crud import create_user  # create_mutualfund must exist if used
from .database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/users/", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

# If you have create_mutualfund implemented elsewhere, keep this; otherwise remove.
# from .crud import create_mutualfund
@router.post("/mutualfunds/", response_model=MutualFundOut)
async def add_mutualfund(mf: MutualFundCreate, db: AsyncSession = Depends(get_db)):
    # return await create_mutualfund(db, mf)
    raise NotImplementedError("create_mutualfund not implemented in crud.py")
