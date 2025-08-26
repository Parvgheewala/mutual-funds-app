# app/crud.py
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.security import hash_password

# -----------------------------
# Create user
# -----------------------------
async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    """
    Create a new user. Username and email are unique.
    Password is hashed before storing.
    """
    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password=hash_password(user_in.password),
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        # Unique constraint violation on username/email
        await db.rollback()
        raise

# -----------------------------
# List users (paginated)
# -----------------------------
async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 50
) -> Sequence[models.User]:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

# -----------------------------
# Get user by ID
# -----------------------------
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

# -----------------------------
# Get user by username (helper)
# -----------------------------
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

# -----------------------------
# Update user (partial)
# -----------------------------
async def update_user(
    db: AsyncSession, user_id: int, user_in: schemas.UserUpdate
) -> Optional[models.User]:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # Apply partial changes
    if user_in.username is not None:
        user.username = user_in.username
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.password is not None and user_in.password != "":
        user.password = hash_password(user_in.password)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise

# -----------------------------
# Delete user
# -----------------------------
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True
