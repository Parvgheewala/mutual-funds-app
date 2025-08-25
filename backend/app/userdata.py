from fastapi import APIRouter
from .schemas import UserCreate, MutualFundCreate, UserOut, MutualFundOut
from .CRUD import create_user, create_mutualfund

router = APIRouter()

@router.post("/users/", response_model=UserOut)
async def register_user(user: UserCreate):
    return await create_user(user)

@router.post("/mutualfunds/", response_model=MutualFundOut)
async def add_mutualfund(mf: MutualFundCreate):
    return await create_mutualfund(mf)
