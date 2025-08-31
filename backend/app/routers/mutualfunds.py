from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="",
    tags=["Mutual Funds"]
)

@router.post("", response_model=schemas.MutualFundOut, status_code=status.HTTP_201_CREATED)
async def create_mutualfund(mf_in: schemas.MutualFundCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_mutualfund(db, mf_in)

@router.get("/{mf_id}", response_model=schemas.MutualFundOut)
async def get_mutualfund(mf_id: int, db: AsyncSession = Depends(get_db)):
    mf = await crud.get_mutualfund_by_id(db, mf_id)
    if not mf:
        raise HTTPException(status_code=404, detail="Mutual fund not found")
    return mf

@router.get("", response_model=List[schemas.MutualFundOut])
async def list_mutualfunds(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await crud.list_mutualfunds(db, skip, limit)

@router.patch("/{mf_id}", response_model=schemas.MutualFundOut)
async def update_mutualfund(mf_id: int, mf_in: schemas.MutualFundUpdate, db: AsyncSession = Depends(get_db)):
    mf = await crud.update_mutualfund(db, mf_id, mf_in)
    if not mf:
        raise HTTPException(status_code=404, detail="Mutual fund not found")
    return mf

@router.delete("/{mf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mutualfund(mf_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_mutualfund(db, mf_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Mutual fund not found")
    return
