# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.exc import IntegrityError

from .. import schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="",  # final path mounted as /api/users
    tags=["Users"],
)

@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await crud.create_user(db, user_in)
        return user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[schemas.UserOut])
async def list_users(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    try:
        users = await crud.list_users(db, skip, limit)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=schemas.UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{user_id}", response_model=schemas.UserOut)
async def update_user(user_id: int, user_in: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    try:
        user = await crud.update_user(db, user_id, user_in)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        ok = await crud.delete_user(db, user_id)
        if not ok:
            raise HTTPException(status_code=404, detail="User not found")
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
