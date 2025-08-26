# app/crud.py
from typing import Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import models, schemas

# ---------- USERS ----------

async def create_user(db: AsyncSession, user_data: schemas.UserCreate) -> models.User:
    user = models.User(**user_data.model_dump())
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
    res = await db.execute(select(models.User).where(models.User.id == user_id))
    return res.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    res = await db.execute(select(models.User).where(models.User.email == email))
    return res.scalar_one_or_none()

async def list_users(db: AsyncSession, skip: int = 0, limit: int = 50) -> Sequence[models.User]:
    res = await db.execute(
        select(models.User).offset(skip).limit(limit).order_by(models.User.id)
    )
    return res.scalars().all()

async def update_user(db: AsyncSession, user_id: int, user_data: schemas.UserUpdate) -> Optional[models.User]:
    data = {
        k: v for k, v in user_data.model_dump(exclude_unset=True).items()
        if v is not None
    }
    if not data:
        return await get_user_by_id(db, user_id)

    await db.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(**data)
    )
    await db.commit()
    return await get_user_by_id(db, user_id)

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    res = await db.execute(delete(models.User).where(models.User.id == user_id))
    await db.commit()
    return res.rowcount > 0

# ---------- MUTUAL FUNDS ----------

async def create_mutualfund(db: AsyncSession, mf_data: schemas.MutualFundCreate) -> models.MutualFund:
    mf = models.MutualFund(**mf_data.model_dump())
    db.add(mf)
    await db.commit()
    await db.refresh(mf)
    return mf

async def get_mutualfund_by_id(db: AsyncSession, mf_id: int) -> Optional[models.MutualFund]:
    res = await db.execute(select(models.MutualFund).where(models.MutualFund.id == mf_id))
    return res.scalar_one_or_none()

async def list_mutualfunds(db: AsyncSession, skip: int = 0, limit: int = 50) -> Sequence[models.MutualFund]:
    res = await db.execute(
        select(models.MutualFund).offset(skip).limit(limit).order_by(models.MutualFund.id)
    )
    return res.scalars().all()

async def update_mutualfund(db: AsyncSession, mf_id: int, mf_data: schemas.MutualFundUpdate) -> Optional[models.MutualFund]:
    data = {k: v for k, v in mf_data.model_dump(exclude_unset=True).items() if v is not None}
    if not data:
        return await get_mutualfund_by_id(db, mf_id)

    await db.execute(
        update(models.MutualFund)
        .where(models.MutualFund.id == mf_id)
        .values(**data)
    )
    await db.commit()
    return await get_mutualfund_by_id(db, mf_id)

async def delete_mutualfund(db: AsyncSession, mf_id: int) -> bool:
    res = await db.execute(delete(models.MutualFund).where(models.MutualFund.id == mf_id))
    await db.commit()
    return res.rowcount > 0
