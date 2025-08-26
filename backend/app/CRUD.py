from sqlalchemy.orm import Session
from typing import Optional, Sequence
from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import models, schemas
from .database import get_db


# ---------- USERS ----------
async def create_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
) -> models.User:
    user = models.User(**user_data.model_dump())
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise


async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> Optional[models.User]:
    res = await db.execute(select(models.User).where(models.User.id == user_id))
    return res.scalar_one_or_none()


async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Optional[models.User]:
    res = await db.execute(select(models.User).where(models.User.email == email))
    return res.scalar_one_or_none()


async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
) -> Sequence[models.User]:
    res = await db.execute(
        select(models.User).offset(skip).limit(limit).order_by(models.User.id)
    )
    return res.scalars().all()


async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
) -> Optional[models.User]:
    data = {
        k: v for k, v in user_data.model_dump(exclude_unset=True).items()
        if v is not None
    }
    if not data:
        return await get_user_by_id(user_id, db)

    await db.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(**data)
    )
    await db.commit()
    return await get_user_by_id(user_id, db)


async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> bool:
    res = await db.execute(delete(models.User).where(models.User.id == user_id))
    await db.commit()
    return res.rowcount > 0


# ---------- MUTUAL FUNDS ----------
async def create_mutualfund(
    mf_data: schemas.MutualFundCreate,
    db: AsyncSession = Depends(get_db)
) -> models.MutualFund:
    mf = models.MutualFund(**mf_data.model_dump())
    db.add(mf)
    await db.commit()
    await db.refresh(mf)
    return mf


async def get_mutualfund_by_id(
    mf_id: int,
    db: AsyncSession = Depends(get_db)
) -> Optional[models.MutualFund]:
    res = await db.execute(select(models.MutualFund).where(models.MutualFund.id == mf_id))
    return res.scalar_one_or_none()


async def list_mutualfunds(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
) -> Sequence[models.MutualFund]:
    res = await db.execute(
        select(models.MutualFund).offset(skip).limit(limit).order_by(models.MutualFund.id)
    )
    return res.scalars().all()


async def update_mutualfund(
    mf_id: int,
    mf_data: schemas.MutualFundUpdate,
    db: AsyncSession = Depends(get_db)
) -> Optional[models.MutualFund]:
    data = {k: v for k, v in mf_data.model_dump(exclude_unset=True).items()}
    if not data:
        return await get_mutualfund_by_id(mf_id, db)

    await db.execute(
        update(models.MutualFund)
        .where(models.MutualFund.id == mf_id)
        .values(**data)
    )
    await db.commit()
    return await get_mutualfund_by_id(mf_id, db)


async def delete_mutualfund(
    mf_id: int,
    db: AsyncSession = Depends(get_db)
) -> bool:
    res = await db.execute(delete(models.MutualFund).where(models.MutualFund.id == mf_id))
    await db.commit()
    return res.rowcount > 0


def get_mutualfunds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MutualFund).offset(skip).limit(limit).all()
