from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_user(db, user_in)
    except Exception:  # IntegrityError works too if imported
        raise HTTPException(status_code=400, detail="Email already exists")

@router.get("/{user_id}", response_model=schemas.UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/by-email/{email}", response_model=schemas.UserOut)
async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("", response_model=List[schemas.UserOut])
async def list_users(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await crud.list_users(db, skip, limit)

@router.patch("/{user_id}", response_model=schemas.UserOut)
async def update_user(user_id: int, user_in: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return
